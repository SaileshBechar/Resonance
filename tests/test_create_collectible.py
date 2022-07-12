from brownie import interface, config, network
from scripts.helpful_scripts import get_account, fund_with_link
from scripts.deploy import deploy_resonance
from scripts.create_collectible import generateRandomNums

def test_can_create_and_cleanup_collectible():
    deployer = get_account()

    # Deploy
    resonance = deploy_resonance()

    # Create Collectible
    fund_with_link(resonance.address)

    generateRandomNums(deployer, resonance)

    tx_mint = resonance.mint_nf_artwork({"from":deployer})
    tx_mint.wait(1)

    scarcity = tx_mint.events["scarcityAssigned"]["scarcity"]
    item_id = resonance.item_counter()
    print("Scarcity of item {} is {}".format(item_id, scarcity))

    assert resonance.item_counter() == 2

    assert resonance.randomNums(0) % 3 == scarcity

    deployer_balance = resonance.balanceOf(deployer, 0, {"from":deployer})    
    calc_currency_transfered = 1 if resonance.randomNums(1) % 2 < 1 else 0
    assert calc_currency_transfered == deployer_balance

    # Clean up
    link_before = interface.LinkTokenInterface(config["networks"][network.show_active()]["link_token"]).balanceOf(
        deployer, {"from": deployer}
    )
    tx_cancel = resonance.cancelSubscription(deployer, {"from":deployer})
    tx_cancel.wait(1)

    link_after = interface.LinkTokenInterface(config["networks"][network.show_active()]["link_token"]).balanceOf(
        deployer, {"from": deployer}
    )
    assert link_after > link_before






