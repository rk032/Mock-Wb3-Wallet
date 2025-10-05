from mnemonic import Mnemonic
from eth_account import Account
from eth_account.messages import encode_defunct
import secrets

class WalletManager:
    def __init__(self):
        self.mnemo = Mnemonic("english")
    
    def generate_mnemonic(self):
        return self.mnemo.generate(strength=128) 
    
    def from_mnemonic(self, mnemonic):
        if not self.mnemo.check(mnemonic):
            raise ValueError("Invalid mnemonic")
        seed = self.mnemo.to_seed(mnemonic)
        account = Account.from_key(seed[:32])
        return type('Wallet', (), {'address': account.address, 'private_key': account.key.hex()})()
    
    def sign_message(self, private_key_hex, message):
        account = Account.from_key(bytes.fromhex(private_key_hex))
        signed = account.sign_message(encode_defunct(text=message))

        return signed.signature.hex()
