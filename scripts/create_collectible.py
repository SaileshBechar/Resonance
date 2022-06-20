from brownie import Resonance
from scripts.helpful_scripts import get_account, fund_with_link

def main():
    deployerAddress = get_account()
    resonance_token = Resonance[-1]
    fund_with_link(account=deployerAddress, )
    txn_mint = resonance_token.mint(7, {"from":deployerAddress})
    txn_mint.wait(1)