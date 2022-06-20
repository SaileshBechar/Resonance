# from brownie import config, Popularity, network
# from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
import requests
import json

# def main():
    # Get Spotify Auth Token
    # 'Authorization' : 'Basic ' + config["spotify"]["base64client"]
headers = {
    'Authorization' : 'Basic MTQwMTEzZmRkNTlmNGI2YWJmYWNjYzUwNzJiMTEwNTE6ODRlMDI4NDA5YzJhNDc2ZWFkMDhmZTBmNmE1OTY5Yzk='
}
data = {'grant_type':'client_credentials'}
response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
authToken = response.status_code
print(authToken)
    # deployerAddress = get_account()
    # popularityAPI = Popularity.deploy({"from":deployerAddress})
    # volumeTxn = popularityAPI.requestVolumeData()
    # volumeTxn.wait(1)
    # print(popularityAPI.volume)