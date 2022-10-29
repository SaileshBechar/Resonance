from brownie import config, Resonance, network
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS


def test_transfer(token, address1, address2, item_id=0):
    print("Deployer balance before", token.balanceOf(address1, item_id))
    print("Artist balance before", token.balanceOf(address2, item_id))

    token.safeTransferFrom(address1, address2, item_id, 1, "0x0")
    print("Deployer balance after", token.balanceOf(address1, item_id))
    print("Artist balance after", token.balanceOf(address2, item_id))

def deploy_resonance():
    deployerAddress = get_account()
    resonance_token = Resonance.deploy(
        config["networks"][network.show_active()]['vrf_coordinator'],
        config["networks"][network.show_active()]['link_token'],
        config["networks"][network.show_active()]['key_hash'],
        {"from":deployerAddress}, publish_source=config["networks"][network.show_active()]['verify'])
    item_id = resonance_token.item_counter()
    
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        artistAddress = get_account(1)
        test_transfer(resonance_token, deployerAddress, artistAddress, item_id=item_id)
    else:
        print(f'The contract has been successfully deployed at https://testnets.opensea.io/assets/goerli/{resonance_token}/{item_id-1}')
        print(f"Subscription Manager: https://vrf.chain.link/goerli/{resonance_token.s_subscriptionId()}")
    return resonance_token

def main():
    deploy_resonance()