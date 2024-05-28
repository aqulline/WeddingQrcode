import re
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
from kivymd.uix.list import OneLineListItem, TwoLineIconListItem, TwoLineListItem, IconLeftWidget
from pyzbar.pyzbar import decode
from kivymd.toast import toast
from camera4kivy import Preview
from kivymd.uix.textfield import MDTextField

from database import FireBase as FB

Window.keyboard_anim_args = {"d": .2, "t": "linear"}
Window.softinput_mode = "below_target"
Clock.max_iteration = 250

if utils.platform != 'android':
    Window.size = (412, 732)


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

    roles = ['Admin', 'Customer']

    # screen
    screens = ['home']
    screens_size = NumericProperty(len(screens) - 1)
    current = StringProperty(screens[len(screens) - 1])

    # user
    guest_name = StringProperty("loading...")
    guest_number = StringProperty("loading...")
    ceremony_name = StringProperty("loading...")
    guest_id = StringProperty("loading...")
    guest_data = DictProperty({})

    # fetched
    guest_scanned = StringProperty("")
    guest_fetch_name = StringProperty("")
    guest_fetch_phone = StringProperty("")
    guest_datas = {}

    # report
    ceremony_report = {}
    total_guest = StringProperty("")
    total_attended = StringProperty("")

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

    def get_guest(self, phone, name, ceremony_name):
        print(phone, name, ceremony_name)
        self.ceremony_name = ceremony_name
        self.guest_name = name
        self.guest_number = phone
        self.guest_id = self.generate_guest_id()
        self.qr_code(self.guest_id, self.guest_number)

        FB.add_attender(FB(), self.guest_number, self.guest_name, self.guest_id, self.ceremony_name)

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

                thr = threading.Thread(target=self.get_data)
                thr.start()

    def get_data(self):
        barcode = self.root.ids.pda.text
        self.guest_data = FB.search_id(FB(), barcode)
        if self.guest_data:
            self.guest_fetch_name = self.guest_data['user_name']
            self.guest_fetch_phone = self.guest_data['user_phone']
            self.guest_scanned = str(self.guest_data['scanned'])
            Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)

    def verify_user(self, gen_id):
        FB.scan_guest(FB(), gen_id)

    def scan_user_optimize(self):
        self.spin_dialog()
        thr = threading.Thread(target=self.scan_user)
        thr.start()

    def scan_user(self):
        barcode = self.root.ids.pda.text
        FB.scan_guest(FB(), barcode)
        self.get_data()

    def ceremony_report_optimize(self):
        self.spin_dialog()
        # thr = threading.Thread(target=self.ceremony_reports)
        # thr.start()

        Clock.schedule_once(lambda dt: self.ceremony_reports(), 0)

    def ceremony_reports(self):
        report_list = self.root.ids.report_list
        ceremony_report = FB.ceremony_report(FB(), "666")

        self.total_guest = str(ceremony_report['total_guest'])
        self.total_attended = str(ceremony_report['attended_guest'])
        for guest in ceremony_report['not_attended']:
            item = TwoLineIconListItem(text=guest['name'], secondary_text=guest['phone'])
            item.add_widget(IconLeftWidget(icon="phone"))
            item.bind(on_release=lambda x: print(guest['phone']))
            report_list.add_widget(item)
        Clock.schedule_once(lambda dt: self.dialog_spin.dismiss(), 0)

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
