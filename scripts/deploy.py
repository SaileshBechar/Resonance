from brownie import config, Resonance, network
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS


def transfer(token, address1, address2, item_id=0):
    print("Deployer balance before", token.balanceOf(address1, item_id))
    print("Artist balance before", token.balanceOf(address2, item_id))

    token.safeTransferFrom(address1, address2, item_id, 1, "0x0")
    print("Deployer balance after", token.balanceOf(address1, item_id))
    print("Artist balance after", token.balanceOf(address2, item_id))

def main():
    deployerAddress = get_account()
    resonance_token = Resonance.deploy({"from":deployerAddress}, publish_source=True)
    item_id = resonance_token.item_counter()
    
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        artistAddress = get_account(1)
        transfer(resonance_token, deployerAddress, artistAddress, item_id=item_id)
    else:
        print(f'The contract has been successfully deployed at https://testnets.opensea.io/assets/rinkeby/{resonance_token}/{item_id}')
        print(f"Subscription Manager: https://vrf.chain.link/rinkeby/{resonance_token.s_subscriptionId()}")