from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

contract_address = "YOUR_CONTRACT_ADDRESS"
abi = []  # paste ABI here

contract = w3.eth.contract(address=contract_address, abi=abi)

def send_donation(account, private_key, amount):
    tx = contract.functions.donate().build_transaction({
        'from': account,
        'value': w3.to_wei(amount, 'ether'),
        'nonce': w3.eth.get_transaction_count(account),
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    return w3.eth.send_raw_transaction(signed_tx.rawTransaction)