from brownie import Resonance
from scripts.helpful_scripts import get_account, fund_with_link, get_scarcity, listen_for_event
from web3 import Web3

def main():
    deployerAddress = get_account()
    resonance_token = Resonance[-1]

    # 1. Fund Contract
    fund_with_link(resonance_token.address) # Fund contract with at least 3 LINK
    
    # 2. Generate Random Values from Chainlink VRF
    tx_rand = resonance_token.generateRandomWords({"from":deployerAddress})
    tx_rand.wait(1)
    listen_for_event(
        resonance_token, "randomWordsGenerated", timeout=300, poll_interval=10
    )
    print("Random nums", resonance_token.randomNums(0), resonance_token.randomNums(1))

    # tx_mint = resonance_token.mint_nf_artwork(deployerAddress, {"from":deployerAddress})
    # tx_mint.wait(1)
    # print(f"You have created {resonance_token.item_counter()} tokens")

    # tx_transfer = resonance_token.transfer_currency(deployerAddress, {"from":deployerAddress})
    # tx_transfer.wait(1)

    # requestId = tx_mint.events["requestedCollectible"]["requestId"]
    item_id = resonance_token.item_counter()
    scarcity = get_scarcity(resonance_token.itemIdToScarcity(item_id))
    print("Scarcity of item {} is {}".format(item_id, scarcity))