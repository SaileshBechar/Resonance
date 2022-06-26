# from brownie import config, Popularity, network
# from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
import requests
import json

headers = {
    'Authorization' : 'Basic MTQwMTEzZmRkNTlmNGI2YWJmYWNjYzUwNzJiMTEwNTE6ODRlMDI4NDA5YzJhNDc2ZWFkMDhmZTBmNmE1OTY5Yzk='
}
data = {'grant_type':'client_credentials'}
auth_response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
authToken = auth_response.json()['access_token']
print(authToken)
# headers = {
#     "Authorization: Bearer " + authToken
# }
# artist_response = requests.get('https://api.spotify.com/v1/artists/1ZtRTibAPAEbO8iydpyzWu', headers=headers)
# print(artist_response.json()['popularity'])