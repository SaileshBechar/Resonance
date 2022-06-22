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

SCARCITY_MAPPING = {0 : "COMMON", 1 : "RARE", 2 : "ULTRA_RARE"}

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        print(accounts[0].balance())
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])

def get_scarcity(scarcity_idx):
    return SCARCITY_MAPPING[scarcity_idx]

def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    contract_address = config["networks"][network.show_active()][contract_name]
    print(network.show_active(), contract_name, contract_address)
    contract = Contract.from_abi(
        contract_type._name, contract_address, contract_type.abi
    )
    return contract

def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):
    account = account if account else get_account()
    # link_token = link_token if link_token else get_contract("link_token")
    link_token_address = config["networks"][network.show_active()]["link_token"]
    tx = interface.LinkTokenInterface(link_token_address).transfer(
        contract_address, amount, {"from": account}
    )
    tx.wait(1)
    print(f"Funded {contract_address}")
    return tx