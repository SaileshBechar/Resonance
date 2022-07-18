from brownie import interface, config, network
from scripts.helpful_scripts import get_account, fund_with_link
from scripts.deploy import deploy_resonance
from scripts.create_collectible import generateRandomNums
import time

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
    print(f'{link_after - link_before} added back to {deployer}')

def test_popularity():
    deployer = get_account()
    
    artist_1 = deploy_resonance()
    a1_popularity = []
    for i in range(5):
        fund_with_link(artist_1.address)

        generateRandomNums(deployer, artist_1)

        tx_mint = artist_1.mint_nf_artwork({"from":deployer})

        a1_popularity.append(tx_mint.events["popularityAssigned"]["popularity"])

    print("Artist 1 Minted")
    tx_cancel = artist_1.cancelSubscription(deployer, {"from":deployer})
    tx_cancel.wait(1)

    artist_2 = deploy_resonance()
    a2_popularity = []
    for i in range(5):
        fund_with_link(artist_2.address)

        generateRandomNums(deployer, artist_2)

        tx_mint = artist_2.mint_nf_artwork({"from":deployer})

        a2_popularity.append(tx_mint.events["popularityAssigned"]["popularity"])

        time.sleep(60)
    
    tx_cancel = artist_2.cancelSubscription(deployer, {"from":deployer})
    tx_cancel.wait(1)
    print("Artist 2 Minted")
    
    artist_3 = deploy_resonance()
    a3_popularity = []
    for i in range(5):
        fund_with_link(artist_3.address)

        generateRandomNums(deployer, artist_3)

        tx_mint = artist_3.mint_nf_artwork({"from":deployer})

        a3_popularity.append(tx_mint.events["popularityAssigned"]["popularity"])

        time.sleep(180)

    print("Artist 1 Popularity:", a1_popularity)
    print("Artist 2 Popularity:", a2_popularity)
    print("Artist 3 Popularity:", a3_popularity)

    for i in range(5):
        assert a1_popularity[i] >= a2_popularity[i]
        assert a2_popularity[i] >= a3_popularity[i]

    
    tx_cancel = artist_3.cancelSubscription(deployer, {"from":deployer})
    tx_cancel.wait(1)

