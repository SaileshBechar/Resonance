from pathlib import Path
import os, requests

def main():
    PINATA_BASE_URL = "https://api.pinata.cloud/"
    endpoint = "pinning/pinFileToIPFS"
    file_path="./img/Dance_with_Divine.png"
    file_name = file_path.split('/')[-1:][0]
    headers = {
        "pinata_api_key" : os.getenv("PINATA_API"), 
        "pinata_secret_api_key" : os.getenv("PINATA_SECRET")
    }
    with Path(file_path).open("rb") as fp:
        img_bin = fp.read()
        response = requests.post(PINATA_BASE_URL + endpoint, files={"file":(file_name, img_bin)}, headers=headers)
    print(response.json())