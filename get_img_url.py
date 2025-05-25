import base64

import requests

class ImageMethods:
    def encode_img(self, file_path):
        image = open(file_path, 'rb')
        image_read = image.read()
        image_64_encode = base64.encodebytes(image_read)  # encodestring also works aswell as decodestring

        return image_64_encode

    def get_url(self, file_path):
        url = "https://api.imgbb.com/1/upload"
        params = {
            "expiration": 600,  # Image expiration time in seconds
            "key": "efb881e489dc1043fd469074797dcd03"  # Replace with your actual API key
        }
        image_base64 = self.encode_img(file_path)
        data = {
            "image": image_base64

        }
        response = requests.post(url, params=params, data=data)
        if response.status_code == 200:
            print("Image uploaded successfully!")
            print("Response:", response.json())
            data = response.json()
            url = data['data']["url"]

            return url