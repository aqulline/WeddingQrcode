import requests
from credential import whapicred
from get_img_url import ImageMethods as IM

class Whatsapp:
    # send_of_name = 'Titus Tumaini Massawe'

    def send_image(self, phone_number, text_sms):
        zaniel = '255676133153'
        url = f"https://gate.whapi.cloud/messages/media/image"

        # payload = {"media": IM.get_url(IM(), f'Qrcodes/{phone_number}.png')}
        payload = {
            "to": zaniel,
            "media": IM.get_url(IM(), f'Qrcodes/{phone_number}.png'),
            "caption": text_sms
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer ZBiEln7aS1JvgyaT8J9HthF9p5h0dLLY"
        }

        response = requests.post(url, json=payload, headers=headers)

        print(response.text)

    def send_card(self, phone_number, guest_number, text_sms):
        url = "https://gate.whapi.cloud/messages/image"

        # payload = {"media": IM.get_url(IM(), f'cards/0715700411.png')}
        payload = {
            "to": phone_number,
            "media": IM.get_url(IM(), f'Cards5/{guest_number}.png'),
            "caption": text_sms
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer ZBiEln7aS1JvgyaT8J9HthF9p5h0dLLY"
        }

        response = requests.post(url, json=payload, headers=headers)

        print(response.text)

    def send_invitation(self, phone_number, guest_number, guest_name):
        # self.send_message(phone_number, f"Umealikwa kwenye Sendoff ya Familia ya bwana {self.send_of_name} Itakayo fanyika tarehe 29/11/2024")
        # self.send_message(phone_number, "Kama uta huthuria tuma neno 'ATTENDING' kama huta udhuria tuna neno 'NOT ATTENDING' ")
        self.send_card(phone_number, guest_number, f'KADI YA Sendoff \nFamilia ya Bwana Willix Kabonge Wa Kimara Bonyokwa. Inapenda/Wanapenda kukualika MR/MRs *{guest_name}* kwenye sendoff ya Binti yao mpendwa Jackline W Kabonge itakayofanyika *Tarehe 15-01-2025 Saa 12 JIONI*.\nUkumbi: *TANZANITE-KIMARA-korogwe-resort*\nTafadhali, Kumbuka kufika na kadi hii mlangoni.\nKaribu sana\n' 
                                                   f'Mawasiliano:0755011139/0754679386\n*e_cards_tz*')
        self.send_poll(phone_number)



    def interactive_sms(self, phone_number):
        url = "https://gate.whapi.cloud/messages/interactive"

        payload = {
            "header": {"text": "Chagua Neno Moja hapo Chini"},
            "body": {"text": "Kama uta huthuria chagua neno 'ATTENDING' kama huta udhuria chagua neno 'NOT ATTENDING' "},
            "footer": {"text": "AlphaSmartCard"},
            "action": {
                "list": {
                    "label": "Going",
                    "sections": [{"title": "Going wedding"}]
                },
                "buttons": [
                    {
                        "type": "quick_reply",
                        "title": "ATTENDING",
                        "id": "90"
                    },
                    {
                        "type": "quick_reply",
                        "title": "NOT ATTENDING",
                        "id": "91"
                    },
                ]
            },
            "type": "button",
            "to": f"{phone_number}@s.whatsapp.net",
            "view_once": True
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {whapicred.Berier}"
        }

        response = requests.post(url, json=payload, headers=headers)

        return response

    def send_message(self, phone, text_message):
        # URL to send messages through the Whapi.Cloud API
        url = f"https://gate.whapi.cloud/messages/text?token={whapicred.Berier}"

        # Forming the body of the message
        payload = {
            "to": phone,
            "body": text_message
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        # Sending the message
        response = requests.post(url, json=payload, headers=headers)
        return response

    def send_poll(self, phone_number):

        url = "https://gate.whapi.cloud/messages/poll"

        payload = {
            "options": ["Sitoweza kufika", "Asante, Nitafika"],
            "to": phone_number,
            "title": "TUNAOMBA UTHIBITISHE UWEPO WAKO KWA KUCHAGUA KIMOJA WAPO HAPA CHINI, ASANTE!",
            "count": 1
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer ZBiEln7aS1JvgyaT8J9HthF9p5h0dLLY"
        }

        response = requests.post(url, json=payload, headers=headers)

        print(response.text)

# Whatsapp.send_message(Whatsapp(), "255654327335", 'Hello')
# Whatsapp.send_card(Whatsapp(), '255676133153', '0715700411', "fika na hii xard")
# Whatsapp.send_image(Whatsapp(), '0715700411', 'Aqulline')