import re
import string
from datetime import datetime
import threading

from PIL import Image
from kivy.base import EventLoop
from kivy.properties import NumericProperty, StringProperty, DictProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy import utils
import qrcode
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget, TwoLineAvatarIconListItem, IRightBodyTouch, \
    ThreeLineAvatarIconListItem
from pyzbar.pyzbar import decode
from kivymd.toast import toast
from camera4kivy import Preview
from kivymd.uix.textfield import MDTextField

from tsup_media import Whatsapp as WS
from database import FireBase as FB

Window.keyboard_anim_args = {"d": .2, "t": "linear"}
Window.softinput_mode = "below_target"
Clock.max_iteration = 250

if utils.platform != 'android':
    Window.size = (412, 732)

class Contacts(ThreeLineAvatarIconListItem):
    name = StringProperty("")
    image = StringProperty("")
    contact_id = StringProperty("")
    phone = StringProperty("")
    whatsapp_status = StringProperty("Default")
    normal_status = StringProperty("False")

class CallContainer(IRightBodyTouch, MDBoxLayout):
    adaptive_width = True

class Spin(MDBoxLayout):
    pass

class Admin(FloatLayout):
    pass

class Ceremony(FloatLayout):
    pass

class Front(MDCard):
    pass



class Scan_Analyze(Preview):
    extracted_data = ObjectProperty(None)

    def analyze_pixels_callback(self, pixels, image_size, image_pos, scale, mirror):

        pimage = Image.frombytes(mode='RGBA', size=image_size, data=pixels)
        list_of_all_barcodes = decode(pimage)

        if list_of_all_barcodes:
            if self.extracted_data:
                self.extracted_data(list_of_all_barcodes[0])
            else:
                print("NOt found")


class NumberOnlyField(MDTextField):
    pat = re.compile('[^0-9]')

    input_type = "number"

    def insert_text(self, substring, from_undo=False):

        pat = self.pat

        if "." in self.text:
            s = re.sub(pat, "", substring)

        else:
            s = ".".join([re.sub(pat, "", s) for s in substring.split(".", 1)])

        return super(NumberOnlyField, self).insert_text(s, from_undo=from_undo)


class MainApp(MDApp):
    # app
    size_x, size_y = Window.size
    dialog_spin = None
    is_admin = BooleanProperty(False)
    admin_pos_x = NumericProperty(.5)
    admin_pos_y = NumericProperty(.04)

    roles = ['Admin', 'Customer']

    # screen
    screens = ['home']
    screens_size = NumericProperty(len(screens) - 1)
    current = StringProperty(screens[len(screens) - 1])

    # user
    guest_name = StringProperty("loading...")
    guest_number = StringProperty("loading...")
    ceremony_name = StringProperty("EMS")
    guest_id = StringProperty("loading...")
    guest_data = DictProperty({})
    isDouble = False

    # fetched
    guest_scanned = StringProperty("")
    guest_fetch_name = StringProperty("")
    guest_fetch_phone = StringProperty("")
    guest_type = StringProperty("")
    # guest_datas = {}
    story = StringProperty("")

    # report
    ceremony_report = {}
    total_guest = StringProperty("0")
    total_attended = StringProperty("0")
    total_confirmed = StringProperty("0")
    title_data = StringProperty("")
    data_getter = StringProperty("all_guests")

    #Guest Report
    attend_time = StringProperty('Not Yet')
    guest_phone = StringProperty('Not Yet')
    guest_name_r = StringProperty("Not Yet")
    confirmed_status = BooleanProperty(False)


    def on_start(self):
        if utils.platform == 'android':
            self.request_android_permissions()
        self.keyboard_hooker()

    def keyboard_hooker(self, *args):
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *largs):
        print(self.screens_size)
        if key == 27 and self.screens_size > 0:
            print(f"your were in {self.current}")
            last_screens = self.current
            self.screens.remove(last_screens)
            print(self.screens)
            self.screens_size = len(self.screens) - 1
            self.current = self.screens[len(self.screens) - 1]
            self.screen_capture(self.current)
            return True
        elif key == 27 and self.screens_size == 0:
            toast('Press Home button!')
            return True

    def spin_dialog(self):
        if not self.dialog_spin:
            self.dialog_spin = MDDialog(
                type="custom",
                auto_dismiss=False,
                size_hint=(.43, None),
                content_cls=Spin(),
            )
        self.dialog_spin.open()

    def generate_guest_id(self):
        # timestamp = int(time() * 1000)  # Convert current time to milliseconds
        refer = str(datetime.now())
        refer = refer.replace('-', '').replace(':', '').replace(' ', '').replace('.', '')
        return str(refer)

    def toggle_double(self, active):
        print(active.active)
        if active.active == True:
            active.active = False
            print(f"Set {active.active} to False")
            return False
        if active.active == False:
            active.active = True
            print(f"Set {active.active} to True")
            return True

    def add_attender_opt(self):
        self.spin_dialog()
        thr = threading.Thread(target=self.add_attenders)
        thr.start()

    def phone_repr(self, phone):
        new_number = ""
        if phone != "" and len(phone) != 9:
            for i in range(phone.__len__()):
                if i == 0:
                    pass
                else:
                    new_number = new_number + phone[i]
            number = "255" + new_number
            public_number = number
            return public_number
        return False

    def add_attenders(self):
        FB.add_attender(FB(), self.guest_number, self.guest_name, self.guest_id, self.ceremony_name, self.isDouble)
        phone = self.phone_repr(self.guest_number)
        if phone:
            WS.send_image(WS(), self.guest_number, f"{self.guest_name} {self.guest_number} Ni double {self.isDouble}")
            WS.send_invitation(WS(), phone, self.guest_number, self.guest_name)
        else:
            Clock.schedule_once(lambda dt: toast("Check phone number!"), 0)
        Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
        Clock.schedule_once(lambda dt: toast("Guest added successful!"), 0)

    def guest_report(self, guest_phone):
        data = FB.search_idex_phone(FB(), guest_phone, self.ceremony_name)
        print(data)
        self.guest_name_r = data.get("User_Info").get("user_name", '')
        self.guest_phone = data.get("User_Info").get("user_phone", '')
        self.attend_time = data.get("User_Info").get("scanned_time", 'Not Yet')
        confirmed = data.get("User_Info").get("confirmed", 0)
        self.confirmed_status = False if confirmed==0 else True
        print(self.confirmed_status)

    def guest_confirmed(self, status, guest_phone):
        if status:
            local_status = 1
        else:
            local_status = 0
        data = FB.confirm_guest(FB(), self.ceremony_name, guest_phone, local_status)
        if data['status'] == 200:
            toast("User status changed")

    def get_guest(self, phone, name, ceremony_name, isDouble):
        print(phone, name, ceremony_name)
        self.ceremony_name = ceremony_name
        self.guest_name = name
        self.guest_number = phone
        self.guest_id = self.generate_guest_id()
        self.qr_code(self.guest_id, self.guest_number)
        self.isDouble = isDouble

        # FB.add_attender(FB(), self.guest_number, self.guest_name, self.guest_id, self.ceremony_name, isDouble)

    def qr_code(self, id_gen, phone):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(id_gen)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"Qrcodes/{phone}.png")

    def get_details(self):
        self.root.ids.details_scan.connect_camera(enable_analyze_pixels=True, default_zoom=0.0)
        print("connected")

    def stop_camera_detail(self):
        self.root.ids.details_scan.disconnect_camera()

    @mainthread
    def get_QRcode(self, result):
        barcode = str(result.data)
        code_type = str(result.type)
        print(barcode)
        if barcode:
            if code_type == "QRCODE":
                barcode = barcode.replace("b", "").replace("'", "")

                self.root.ids.pda.text = barcode

                self.spin_dialog()
                # guest_data = FB.search_id(FB(), barcode)
                self.screen_capture("Confirm")
                thr = threading.Thread(target=self.get_data)
                thr.start()

    def get_data(self):
        barcode = self.root.ids.pda.text
        # guest_data = FB.search_idex(FB(), barcode, self.ceremony_name)
        guest_data = FB.get_guest(FB(), barcode.lstrip(string.ascii_uppercase))
        if guest_data[1] == 200:
            if guest_data:
                self.guest_fetch_name = guest_data[0]['guest_name']
                self.guest_fetch_phone = guest_data[0]['guest_phone']
                self.guest_scanned = '1' if guest_data[0]['attended'] else '0'
                self.guest_type = guest_data[0]['card_type']
                if self.dialog_spin:
                    Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)
        else:
            toast("Guest not found.")
            self.screen_leave()

    def verify_user(self, gen_id):
        print(gen_id)

    def scan_user_optimize(self):
        self.spin_dialog()
        thr = threading.Thread(target=self.scan_user)
        thr.start()

    def scan_user(self):
        barcode = self.root.ids.pda.text
        data = FB.scan_guest_API(FB(), barcode.lstrip(string.ascii_uppercase))
        Clock.schedule_once(lambda dt: toast(data['message']), 0)
        self.get_data()

    def ceremony_report_optimize(self):
        self.spin_dialog()
        # thr = threading.Thread(target=self.ceremony_reports)
        # thr.start()

        Clock.schedule_once(lambda dt: self.ceremony_reports(), 0)

    guest_datas = DictProperty({})
    def ceremony_reports(self):
        report_list = self.root.ids.report_list
        self.ceremony_name = FB.get_ceremony_name(FB())['data']
        ceremony_report = FB.ceremony_report(FB(), self.ceremony_name)

        print(ceremony_report)
        self.guest_datas = ceremony_report
        self.total_guest = str(ceremony_report['total_guest'])
        self.total_attended = str(ceremony_report['attended_guest'])
        self.total_confirmed = str(ceremony_report['total_confirmed'])
        # Clock.schedule_once(lambda dt: self.load_contacts_to_ui(ceremony_report), 0)
        Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)

    # for guest in ceremony_report['not_attended']:
    #     item = TwoLineIconListItem(text=guest['name'], secondary_text=guest['phone'])
    #     item.add_widget(IconLeftWidget(icon="account"))
    #     item.bind(on_release=lambda x: print(guest['phone']))
    #     report_list.add_widget(item)

    def search_data(self, text):
        """Helper function to load contacts into the UI."""
        self.root.ids.guests.data = {}

        index = 0
        for guest in self.guest_datas[self.data_getter]:
            if text in guest['name'] or text in guest['phone']:
                self.root.ids.guests.data.append(
                    {
                        "viewclass": "Contacts",
                        "name": guest['name'],
                        "image": "components/account.png",
                        "id": guest['phone'],
                        "phone": guest['phone'],
                        "text": guest['name'],
                        "secondary": guest['phone'],"whatsapp_status": guest.get('whatsapp_status', 'Default'),
                        "normal_status": str(guest.get('normal_sms', 'False')),

                    }
                )
                index += 1

    def load_contacts_to_ui(self):
        """Helper function to load contacts into the UI."""
        self.root.ids.guests.data = {}

        index = 0
        for guest in self.guest_datas[self.data_getter]:
            self.root.ids.guests.data.append(
                {
                    "viewclass": "Contacts",
                    "name": guest['name'],
                    "image": "components/account.png",
                    "id": guest['phone'],
                    "phone": guest['phone'],
                    "text": guest['name'],
                    "secondary": guest['phone'],
                    "whatsapp_status": guest.get('whatsapp_status', 'Default'),
                    "normal_status": str(guest.get('normal_sms', 'False')),
                }
            )
            index += 1

    def call(self, phone):
        # from call import Actions as AC
        from beem import call as CL
        CL.Actions.call(CL.Actions(), phone)

    def request_android_permissions(self):
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.CAMERA], callback)

    def screen_capture(self, screen):
        sm = self.root
        sm.current = screen
        if screen in self.screens:
            pass
        else:
            self.screens.append(screen)
        print(self.screens)
        self.screens_size = len(self.screens) - 1
        self.current = self.screens[len(self.screens) - 1]
        print(f'size {self.screens_size}')
        print(f'current screen {screen}')

    def screen_leave(self):
        print(f"your were in {self.current}")
        last_screens = self.current
        self.screens.remove(last_screens)
        print(self.screens)
        self.screens_size = len(self.screens) - 1
        self.current = self.screens[len(self.screens) - 1]
        self.screen_capture(self.current)

    def build(self):
        self.theme_cls.material_style = "M3"


MainApp().run()
