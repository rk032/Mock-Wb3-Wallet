from datetime import datetime
from firebase_admin import firestore

class DatabaseManager:
    def __init__(self, firestore_client):
        self.client = firestore_client
        self.wallets = self.client.collection('wallets')
        self.transactions = self.client.collection('transactions')
            
    def add_wallet(self, address, balance):
        self.wallets.document(address).set({'balance': float(balance)})
    
    def get_balance(self, address):
        doc = self.wallets.document(address).get()
        if doc.exists:
            return doc.to_dict()['balance']
        return None
    
    def update_balance(self, address, new_balance):
        self.wallets.document(address).update({'balance': float(new_balance)})
    
    def add_transaction(self, address, sender, recipient, amount, tx_type):
        timestamp = datetime.now()
        self.transactions.document().set({
            'address': address,
            'timestamp': timestamp,
            'sender': sender,
            'recipient': recipient,
            'amount': float(amount),
            'type': tx_type
        })
    
    def get_transaction_history(self, address):
        docs = self.transactions.where('address', '==', address).order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        history = []
        for doc in docs:
            data = doc.to_dict()
            history.append({
                'sender': data['sender'],
                'recipient': data['recipient'],
                'amount': data['amount'],
                'timestamp': data['timestamp'].isoformat(),
                'type': data['type']
            })
        return history
    
    def ensure_recipient_balance(self, recipient):
        balance = self.get_balance(recipient)
        if balance is None:
            self.add_wallet(recipient, 0.0)