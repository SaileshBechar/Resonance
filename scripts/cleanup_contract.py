from brownie import Resonance, config, interface, network
from scripts.helpful_scripts import get_account
from web3 import Web3

def main():
    deployerAddress = get_account()
    resonance_token = Resonance[-1]

    tx_cancel = resonance_token.cancelSubscription(deployerAddress, {"from":deployerAddress})
    
    link_token_address = config["networks"][network.show_active()]["link_token"]
    balance = tx_cancel.events['defundContract']
    print("Remaining balance", balance)
    tx = interface.LinkTokenInterface(link_token_address).transfer(
        deployerAddress, balance, {"from": deployerAddress}
    )
    tx.wait(1)
