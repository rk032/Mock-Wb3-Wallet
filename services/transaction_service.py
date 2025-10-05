import requests
import time
from eth_account import Account
from eth_account.messages import encode_defunct  # New import
from services.database_manager import DatabaseManager

class TransactionService:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.expiry_time = 30  # seconds
    
    def get_eth_from_usd(self, usd_amount):
        url = "https://api.skip.build/v2/fungible/msgs_direct"
        body = {
            "source_asset_denom": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "source_asset_chain_id": "1",
            "dest_asset_denom": "ethereum-native",
            "dest_asset_chain_id": "1",
            "amount_in": int(usd_amount * 1_000_000),
            "chain_ids_to_addresses": {"1": "0x742d35Cc6634C0532925a3b8D4C9db96c728b0B4"},
            "slippage_tolerance_percent": "1",
            "smart_swap_options": {"evm_swaps": True},
            "allow_unsafe": False
        }
        try:
            response = requests.post(url, json=body)
            data = response.json()
            eth_wei = int(data['route']['amount_out'])
            eth_amount = eth_wei / 1e18
            return round(eth_amount, 4), usd_amount
        except Exception as e:
            print(f"API error: {e}")
            return None, None
    
    def create_approval_message(self, sender, recipient, amount, usd=0):
        if usd > 0:
            msg = f"Transfer {amount} ETH (${usd} USD) to {recipient} from {sender}"
        else:
            msg = f"Transfer {amount} ETH to {recipient} from {sender}"
        timestamp = int(time.time())
        return f"{msg} | Expires: {timestamp + self.expiry_time}"
    
    def verify_signature(self, message, signature_hex, sender_address):
        try:
            recovered = Account.recover_message(encode_defunct(text=message), signature=bytes.fromhex(signature_hex))
            return recovered.lower() == sender_address.lower()  
        except Exception as e:
            print(f"Debug - Recovery exception: {e}")
            return False
    
    def process_transfer(self, sender, recipient, amount, usd, signature, message):
       
        try:
            expiry_part = message.split(" | ")[1]
            expiry = int(expiry_part.split(": ")[1])
            if time.time() > expiry:
                return {"success": False, "error": "Signature expired"}
        except:
            return {"success": False, "error": "Invalid message format"}
        
        if not self.verify_signature(message, signature, sender):
            return {"success": False, "error": "Invalid signature"}
        
        sender_balance = self.db.get_balance(sender)
        if sender_balance < amount:
            return {"success": False, "error": "Insufficient funds"}
        
        if usd > 0:
            new_eth, _ = self.get_eth_from_usd(usd)
            if new_eth and abs(new_eth - amount) / amount > 0.01: 
                return {"success": False, "error": "Price changed too much"}
        
        self.db.ensure_recipient_balance(recipient)
        
        self.db.update_balance(sender, sender_balance - amount)
        recipient_balance = self.db.get_balance(recipient)
        self.db.update_balance(recipient, recipient_balance + amount)
        
        self.db.add_transaction(sender, sender, recipient, amount, "sent")
        self.db.add_transaction(recipient, sender, recipient, amount, "received")
        

        return {"success": True}
