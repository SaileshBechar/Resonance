from brownie import Resonance, network, config
from scripts.helpful_scripts import get_account, get_scarcity
from metadata.sample_metadata import metadata_template, currency_template
from pathlib import Path
import requests
import os
import json

scarcity_to_img_uri= {
    "COMMON" : "https://ipfs.io/ipfs/QmXTjbcPzZTiXCqZ287FgzXafGrepEbvzmVFhAnRbitBdC?filename=DWDM-common.png",
    "RARE" : "https://ipfs.io/ipfs/QmRjMWfDdFZy5ySLhAn4nzH1eUgfJeDMkmmW7LspQbdZip?filename=DWDM-rare.png",
    "ULTRA_RARE" : "https://ipfs.io/ipfs/QmbNtkaH67nh45eLfsJ4F2cndaDHudQqZ3HRqKSV95Jq3d?filename=DWDM-ultra_rare.png"
}

def main():
    deployerAddress = get_account()
    resonance_token = Resonance[len(Resonance)-1]
    for item_id in range(resonance_token.item_counter()):
        scarcity = get_scarcity(resonance_token.tokenIdToScarcity(item_id))
        print(scarcity)
        item_id_hex = hex(item_id)[2:]
        metadata_file_name = (
            f'./metadata/{network.show_active()}/{item_id_hex.zfill(64)}.json'
        )
        artwork_metadata = metadata_template
        popularity = get_popularity()
        if Path(metadata_file_name).exists():
            print(f'{metadata_file_name} already exists! Delete it to overwrite')
        else:
            print(f'Creating Metadata file: {metadata_file_name}')
            if (item_id == 0):
                artwork_metadata = currency_template
                img_path = (f'./img/Currency.png')
            else:
                artwork_metadata['attributes'][0]['value'] = popularity
                artwork_metadata['attributes'][1]['value'] = scarcity
                print(artwork_metadata)
                img_path = (f'./img/DWDM-{scarcity.lower()}.png')

            img_uri = None
            if os.getenv("UPLOAD_IPFS") == "true": # Upload image to IPFS
                img_uri = upload_to_ipfs(img_path)
                upload_to_pinata(img_path)
            artwork_metadata["image"] = img_uri if img_uri else scarcity_to_img_uri[scarcity]

            with open(metadata_file_name, "w") as file: # write metadata to json file
                json.dump(artwork_metadata, file)
            # Upload metadata to IPFS
            upload_to_ipfs(metadata_file_name)
            upload_to_pinata(metadata_file_name)

# Get Artist's popularity from Spotify
def get_popularity():
    return 28
    headers = {
        'Authorization' : 'Basic ' + config["spotify"]["base64client"]
    }
    data = {'grant_type':'client_credentials'}
    auth_response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    authToken = auth_response.json()['access_token']
    print(authToken)
    headers = {
        "Authorization: Bearer " + authToken
    }
    artist_response = requests.get('https://api.spotify.com/v1/artists/1ZtRTibAPAEbO8iydpyzWu', headers=headers)
    print(artist_response.json()['popularity'])

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