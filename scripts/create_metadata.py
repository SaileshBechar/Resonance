from brownie import Resonance, network
from scripts.helpful_scripts import get_account, fund_with_link, get_scarcity
from metadata.sample_metadata import metadata_template
from pathlib import Path
import random
import requests
import os

def main():
    deployerAddress = get_account()
    resonance_token = Resonance[len(Resonance)-1]
    for item_id in range(resonance_token.item_counter()):
        if (item_id == 0):
            continue
        scarcity = get_scarcity(resonance_token.tokenIdToScarcity(item_id))
        print(scarcity)
        item_id_hex = hex(item_id)[2:]
        metadata_file_name = (
            f'./metadata/{network.show_active()}/{item_id_hex.zfill(64)}.json'
        )
        artwork_metadata = metadata_template
        popularity = random.randint(0,100)
        if Path(metadata_file_name).exists():
            print(f'{metadata_file_name} already exists! Delete it to overwrite')
        else:
            print(f'Creating Metadata file: {metadata_file_name}')
            artwork_metadata['attributes'][0]['value'] = popularity
            artwork_metadata['attributes'][1]['value'] = scarcity
            print(artwork_metadata)
            img_path = (f'./img/Dance_with_Divine.png')
            # img_uri = upload_to_ipfs(img_path)
            upload_to_pinata(img_path)

def upload_to_ipfs(file_path):
    with Path(file_path).open("rb") as fp:
        img_bin = fp.read()
        ipfs_url = "http://127.0.0.1:5001"
        endpoint = "/api/v0/add"
        response = requests.post(ipfs_url + endpoint, files={"file":img_bin})
        ipfs_hash = response.json()["Hash"]
        file_name = file_path.split("/")[-1:][0]
        img_uri = f"https://ipfs.io/ipfs/{ipfs_hash}?filename={file_name}"
        print(img_uri)
        return img_uri

def upload_to_pinata(file_path):
    PINATA_BASE_URL = "https://api.pinata.cloud/"
    endpoint = "pinning/pinFileToIPFS"
    file_name = file_path.split('/')[-1:][0]
    headers = {
        "pinata_api_key" : os.getenv("PINATA_API_KEY"), 
        "pinata_secret_api_key" : os.getenv("PINATA_SECRET")
    }
    with Path(file_path).open("rb") as fp:
        img_bin = fp.read()
        response = requests.post(PINATA_BASE_URL + endpoint, files={"file":(file_name, img_bin)}, headers=headers)
    print(response.json())