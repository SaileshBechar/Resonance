from brownie import accounts, network, config, interface, Contract, LinkToken, VRFCoordinatorMock, MockOracle
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development",
    "ganache-local",
    "mainnet-fork",
]

contract_to_mock = {
    "link_token": LinkToken,
    "vrf_coordinator": VRFCoordinatorMock,
    "oracle": MockOracle,
}

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        print(accounts[0].balance())
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])

def get_scarcity(random_num):
    if random_num < 1:
        return "ULTRA_RARE"
    elif random_num < 100:
        return "RARE"
    else:
        return "COMMON"

def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    contract_address = config["networks"][network.show_active()][contract_name]
    contract = Contract.from_abi(
        contract_type._name, contract_address, contract_type.abi
    )

def fund_with_link(
    contract_address, account=None, link_token=None, amount=Web3.toWei(0.3, "ether")
):
    account = account if account else get_account()
    tx = interface.LinkTokenInterface(link_token).transfer(
        contract_address, amount, {"from": account}
    )
    print(f"Funded {contract_address}")
    return tx