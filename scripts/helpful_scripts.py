from brownie import (
    accounts,
    config,
    network,
)
import eth_utils


LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache", "mainnet-fork"]

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None


def encode_function_data(initializer=None, *args):
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    else:
        return initializer.encode_input(*args)

def upgrade(
    account,
    proxy,
    newimplementation_address,
    proxy_admin_contract=None, 
    initializer=None, 
    *args
):
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encode_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                newimplementation_address,
                encode_function_call,
                {"from": account}
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, newimplementation_address, {"from": account}
            )
    else:
        if initializer:
            encode_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeAndCall(
                newimplementation_address, encode_function_call, {"from": account}
            )
        else:
            transaction = proxy.upgradeTo(newimplementation_address, {"from": account})
    return transaction