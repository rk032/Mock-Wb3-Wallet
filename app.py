import streamlit as st
import secrets
from dotenv import load_dotenv
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from services.wallet_manager import WalletManager
from services.database_manager import DatabaseManager
from services.transaction_service import TransactionService
from services.notification_service import NotificationService
import requests

load_dotenv()

st.set_page_config(page_title="Mock Web3 Wallet", layout="wide")

if not firebase_admin._apps:
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    if not cred_path:
        st.error("Please set FIREBASE_CREDENTIALS_PATH environment variable to your Firebase service account JSON file path.")
        st.stop()
    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
    except ValueError as e:
        if "already exists" not in str(e).lower():
            raise  
        print("Firebase app already initialized; skipping.")  
client = firestore.client()

if 'wallet' not in st.session_state:
    st.session_state.wallet = None
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager(client)
if 'wallet_mgr' not in st.session_state:
    st.session_state.wallet_mgr = WalletManager()
if 'tx_service' not in st.session_state:
    st.session_state.tx_service = TransactionService(st.session_state.db)
if 'notif_service' not in st.session_state:
    st.session_state.notif_service = NotificationService()  

st.title("💰 Mock Web3 Wallet")


page = st.sidebar.selectbox("Choose a page", ["Wallet Setup", "Balance & Send", "Transaction History"])

if page == "Wallet Setup":
    st.header("Create or Import Wallet")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generate New Wallet"):
            mnemonic = st.session_state.wallet_mgr.generate_mnemonic()
            st.session_state.wallet = st.session_state.wallet_mgr.from_mnemonic(mnemonic)
           
            balance = round(secrets.randbelow(900) / 100 + 1.0, 2)  
            st.session_state.db.add_wallet(st.session_state.wallet.address, balance)
            st.success(f"New wallet created! Mnemonic: {mnemonic}")
            st.warning("Save this mnemonic securely! It's your secret key.")
    
    with col2:
        mnemonic_input = st.text_area("Import Existing Mnemonic (12 words)")
        if st.button("Import Wallet") and mnemonic_input.strip():
            try:
                st.session_state.wallet = st.session_state.wallet_mgr.from_mnemonic(mnemonic_input.strip())
                existing_balance = st.session_state.db.get_balance(st.session_state.wallet.address)
                if existing_balance is None:
                    st.session_state.db.add_wallet(st.session_state.wallet.address, 0.0)
                st.success("Wallet imported successfully!")
            except Exception as e:
                st.error(f"Invalid mnemonic: {e}")

elif page == "Balance & Send" and st.session_state.wallet:
    st.header(f"Wallet Address: {st.session_state.wallet.address}")

    balance = st.session_state.db.get_balance(st.session_state.wallet.address)
    if balance is not None:
        st.metric("Balance", f"{balance} ETH")
    
    st.subheader("Send Transaction")
    recipient = st.text_input("Recipient Address")
    amount_type = st.selectbox("Amount in", ["ETH", "USD"])
    amount = st.number_input("Amount", min_value=0.01, value=0.1)
    
    col3, col4 = st.columns(2)
    with col3:
        if st.button("Get Quote & Prepare Transfer"):
            if not recipient or amount <= 0:
                st.error("Please enter valid recipient and amount.")
                st.stop()
            
            if amount_type == "ETH":
                eth_amount = amount
                usd_equiv = 0  
            else:
                
                eth_amount, usd_equiv = st.session_state.tx_service.get_eth_from_usd(amount)
                if eth_amount is None:
                    st.error("Failed to get quote from API.")
                    st.stop()
                amount = eth_amount 
            
            
            message = st.session_state.tx_service.create_approval_message(
                st.session_state.wallet.address, recipient, amount, usd_equiv
            )
            st.session_state.approval_message = message
            st.session_state.pending_tx = {"recipient": recipient, "amount": amount, "usd": usd_equiv}
            st.info(f"Approval Message: {message}")
            st.info("Click Confirm to sign.")
    
    with col4:
        if 'approval_message' in st.session_state and st.button("Confirm & Sign"):
            try:
                signature = st.session_state.wallet_mgr.sign_message(
                    st.session_state.wallet.private_key, st.session_state.approval_message
                )
                st.session_state.signature = signature
                st.success("Signed! Sending to backend...")
                
                result = st.session_state.tx_service.process_transfer(
                    st.session_state.wallet.address,
                    st.session_state.pending_tx["recipient"],
                    st.session_state.pending_tx["amount"],
                    st.session_state.pending_tx["usd"],
                    st.session_state.signature,
                    st.session_state.approval_message
                )
                if result["success"]:
                    st.session_state.notif_service.send_notification(
                        st.session_state.wallet.address, f"Sent {st.session_state.pending_tx['amount']} ETH to {st.session_state.pending_tx['recipient']}"
                    )
                    st.success("Transaction successful!")
                    del st.session_state.approval_message
                    del st.session_state.pending_tx
                    del st.session_state.signature
                else:
                    st.error(f"Transaction failed: {result['error']}")
            except Exception as e:
                st.error(f"Signing failed: {e}")

elif page == "Transaction History" and st.session_state.wallet:
    st.header("Transaction History")
    history = st.session_state.db.get_transaction_history(st.session_state.wallet.address)
    if history:
        for tx in history:
            with st.expander(f"Tx: {tx['timestamp']} | {tx['type']} {tx['amount']} ETH to {tx['recipient'][:10]}..."):
                st.write(f"From: {tx['sender'][:10]}...")
                st.write(f"To: {tx['recipient'][:10]}...")
                st.write(f"Amount: {tx['amount']} ETH")
                st.write(f"Timestamp: {tx['timestamp']}")
    else:
        st.info("No transactions yet.")

else:

    st.warning("Please set up a wallet first.")
