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
    metadata_arr = []
    for item_id in range(resonance_token.item_counter()):
        scarcity = get_scarcity(resonance_token.itemIdToScarcity(item_id))
        print(scarcity)
        item_id_hex = hex(item_id)[2:]
        metadata_folder = (
            f'metadata/{network.show_active()}/{str(resonance_token.address[2:])}/'
        )
        Path(metadata_folder).mkdir(parents=True, exist_ok=True)
        metadata_file_name = (
            metadata_folder + f'{item_id_hex.zfill(64)}.json'
        )
        artwork_metadata = metadata_template
        popularity = resonance_token.itemIdToPopularity(item_id)
        print("Popularity", popularity)
        if Path(metadata_file_name).exists():
            print(f'{metadata_file_name} already exists! Delete it to overwrite')
        else:
            print(f'Creating Metadata file: {metadata_file_name}')
            if (item_id == 0): # Special case for id = 0 is artist's currency
                artwork_metadata = currency_template
                img_path = (f'./img/Currency.png')
            else:
                artwork_metadata['attributes'][0]['value'] = popularity
                artwork_metadata['attributes'][1]['value'] = scarcity
                artwork_metadata['attributes'][2]['value'] = item_id
                print(artwork_metadata)
                img_path = (f'./img/DWDM-{scarcity.lower()}.png')

                img_uri = None
                if os.getenv("UPLOAD_IPFS") == "true": # Upload image to IPFS
                    img_uri = upload_to_ipfs(img_path)
                    upload_to_pinata(img_path)
                artwork_metadata["image"] = img_uri if img_uri else scarcity_to_img_uri[scarcity]

            with open(metadata_file_name, "w") as file: # write metadata to json file
                json.dump(artwork_metadata, file)
                metadata_arr.append(metadata_file_name)
            # Upload metadata to IPFS
            # upload_to_ipfs(metadata_file_name)
            # upload_to_pinata(metadata_file_name)
    # Upload metadata folder to IPFS
    # upload_to_ipfs(str(resonance_token.address)[2:])
    folder_uri = upload_folder_pinata(metadata_arr, metadata_folder.split('/'))
    print("Folder URI:", folder_uri)
    resonance_token.setURI(folder_uri, {'from':deployerAddress})

def upload_folder_to_ipfs(contract_address):
    ipfs_url = "http://127.0.0.1:5001"
    endpoint = "/api/v0/add"
    headers = {
        'Content-Disposition': f'form-data; name="file"; filename="{contract_address}"',
        "Content-Type": "application/x-directory"
    }
    response = requests.post(ipfs_url + endpoint, headers=headers)
    print("Folder response:", response.json())

def upload_folder_pinata(file_arr, meta_path):
    PINATA_BASE_URL = "https://api.pinata.cloud/"
    endpoint = "pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key" : os.getenv("PINATA_API_KEY"), 
        "pinata_secret_api_key" : os.getenv("PINATA_SECRET")
    }
    print("FILE ARRAY:", file_arr)
    file_data = []
    for file_name in file_arr:
        with Path(file_name).open("rb") as fp:
            print("File Name:", file_name)
            file_data.append(("file",(file_name, fp.read())))
    response = requests.post(PINATA_BASE_URL + endpoint, files=file_data, headers=headers)
    return "ipfs://" + response.json()["IpfsHash"] + "/" + meta_path[1] + "/" + meta_path[2] + "/{id}.json"

def upload_to_ipfs(file_path, contract_address):
    file_name = file_path.split('/')[-1:][0]
    with Path(file_path).open("rb") as fp:
        img_bin = fp.read()
        ipfs_url = "http://127.0.0.1:5001"
        endpoint = "/api/v0/add"
        headers = {
            'Content-Disposition': f'form-data; name="file"; filename="{contract_address}%2F{file_name}"',
            'Content-Type': 'application/octet-stream'
        }
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
    return response.json()