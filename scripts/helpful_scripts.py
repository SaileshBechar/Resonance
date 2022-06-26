from brownie import accounts, network, config, interface, Contract, LinkToken, VRFCoordinatorMock, MockOracle, web3
from web3 import Web3
import time

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
    contract_address, account=None, link_token=None, amount=Web3.toWei(2, "ether")
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

def listen_for_event(brownie_contract, event, timeout=200, poll_interval=2):
    """Listen for an event to be fired from a contract.
    We are waiting for the event to return, so this function is blocking.

    Args:
        brownie_contract ([brownie.network.contract.ProjectContract]):
        A brownie contract of some kind.

        event ([string]): The event you'd like to listen for.

        timeout (int, optional): The max amount in seconds you'd like to
        wait for that event to fire. Defaults to 200 seconds.

        poll_interval ([int]): How often to call your node to check for events.
        Defaults to 2 seconds.
    """
    web3_contract = web3.eth.contract(
        address=brownie_contract.address, abi=brownie_contract.abi
    )
    start_time = time.time()
    current_time = time.time()
    event_filter = web3_contract.events[event].createFilter(fromBlock="latest")
    while current_time - start_time < timeout:
        for event_response in event_filter.get_new_entries():
            if event in event_response.event:
                print("Found event!")
                return event_response
        time.sleep(poll_interval)
        current_time = time.time()
    print("Timeout reached, no event found.")
    return {"event": None}