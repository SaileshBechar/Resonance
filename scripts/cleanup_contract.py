from brownie import Resonance, config, interface, network
from scripts.helpful_scripts import get_account
from web3 import Web3

def main():
    deployerAddress = get_account()
    resonance_token = Resonance[-1]

    resonance_token.cancelSubscription(deployerAddress, {"from":deployerAddress})
    
    link_token_address = config["networks"][network.show_active()]["link_token"]
    tx = interface.LinkTokenInterface(link_token_address).transfer(
        deployerAddress, Web3.toWei(1, "ether"), {"from": deployerAddress}
    )
    tx.wait(1)
    # resonance_token.withdraw(1000000000000000000, config["wallets"]["from_address"], {"from":deployerAddress})
