from web3 import Web3
from eth_account.messages import encode_defunct

def verify_signature(message, signature, wallet_address):
    """
    Verify that a message was signed by the given wallet address.
    
    Args:
        message (str): The original message that was signed
        signature (str): The signature from MetaMask
        wallet_address (str): The wallet address that supposedly signed
    
    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        w3 = Web3()
        
        # Encode the message as per Ethereum standard
        message_hash = encode_defunct(text=message)
        
        # Recover the address from the signature
        recovered_address = w3.eth.account.recover_message(message_hash, signature=signature)
        
        # Compare with the provided wallet address (case-insensitive)
        return recovered_address.lower() == wallet_address.lower()
    except Exception as e:
        print(f"Signature verification error: {str(e)}")
        return False
