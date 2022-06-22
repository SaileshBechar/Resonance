from brownie import Resonance
from scripts.helpful_scripts import get_account, fund_with_link

def main():
    deployerAddress = get_account()
    resonance_token = Resonance[len(Resonance)-1]
    # fund_with_link(resonance_token.address)
    txn_mint = resonance_token.mint(7, {"from":deployerAddress})
    txn_mint.wait(1)
    # listen_for_event(
    #     resonance_token, "requestedCollectible", timeout=200, poll_interval=10
    # )
    # requestId = transaction.events["requestedCollectible"]["requestId"]
    # token_id = resonance_token.requestIdToTokenId(requestId)
    # breed = get_breed(resonance_token.tokenIdToBreed(token_id))
    # print("Dog breed of tokenId {} is {}".format(token_id, breed))
    print(f"You have created {resonance_token.item_counter() + 1} tokens")