import requests
import time
import os


url = "http://127.0.0.1:8000/upload/"
image_path = "Images/dummy.jpg"
while True:
        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            response = requests.post(url, files=files)
            print(f"Status Code: {response.status_code}, Response: {response.text}")
        time.sleep(10)