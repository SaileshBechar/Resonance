from brownie import Resonance
from scripts.helpful_scripts import get_account, fund_with_link, get_scarcity, listen_for_event
from web3 import Web3

def main():
    deployerAddress = get_account()
    resonance_token = Resonance[-1]

    # 1. Fund Contract
    fund_with_link(resonance_token.address) # Fund contract with at least 3 LINK
    
    # 2. Generate Random Values from Chainlink VRF
    generateRandomNums(deployerAddress, resonance_token)

    # 3. Mint Non-Fungible Token and Transfer Fungible Token
    tx_mint = resonance_token.mint_nf_artwork({"from":deployerAddress})
    tx_mint.wait(1)
    print(f"You have created {resonance_token.item_counter()} tokens")

    scarcity = tx_mint.events["scarcityAssigned"]["scarcity"]
    item_id = resonance_token.item_counter()
    print("Scarcity of item {} is {}".format(item_id, scarcity))

def generateRandomNums(deployerAddress, resonance_token):
    tx_top = resonance_token.topUpSubscription(Web3.toWei(12, "ether"), {"from":deployerAddress})
    tx_top.wait(1)
    tx_rand = resonance_token.generateRandomWords({"from":deployerAddress})
    tx_rand.wait(1)
    listen_for_event(
        resonance_token, "randomWordsGenerated", timeout=300, poll_interval=10
    )
    print("Random nums:", resonance_token.randomNums(0), resonance_token.randomNums(1))