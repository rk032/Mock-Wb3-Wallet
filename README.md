# Mock-Wb3-Wallet
A simple, educational mock Ethereum wallet application built with Streamlit. It simulates key Web3 features like wallet creation/import, balance viewing, signed transfers (in ETH or USD equivalents via real-time API quotes), transaction history, and email notifications—all powered by Firebase Firestore for cloud storage.

Features :

Wallet Management: Generate a new 12-word BIP-39 mnemonic or import an existing one to derive an Ethereum address.
Balance Display: View mock ETH balance (random 1-10 ETH on creation).
Send Transfers:

Direct ETH amounts or USD equivalents (fetched via Skip API for real-time pricing).
Requires digital signature approval (using EIP-191) for security.
Verifies signatures, expiry (30s), and price slippage (1% for USD).


Transaction History: View sent/received logs with timestamps.
Notifications: Email alerts on successful transfers (Gmail SMTP).
Cloud Persistence: Balances and history stored in Firebase Firestore.

Tech Stack

Frontend: Streamlit (web UI)
Backend: Python services for wallet derivation (mnemonic, eth-account), transactions, and notifications.
Database: Firebase Firestore (NoSQL, cloud-hosted).
APIs: Skip API (USD-to-ETH quotes).
Libraries: mnemonic (BIP-39), eth-account (signing), requests (HTTP), firebase-admin (DB).

Prerequisites

Python 3.8+ and pip.
Firebase project with Firestore enabled.
Gmail account with 2FA and an app password for notifications (optional).

Setup Instructions

Clone/Setup Project:
textgit clone <your-repo>  # Or create the folder structure
cd mock_web3_wallet
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

Firebase Configuration:

Create a project at console.firebase.google.com.
Enable Firestore (Native mode).
In Project Settings > Service Accounts, generate a private key (JSON file).
Set env var: export FIREBASE_CREDENTIALS_PATH=/path/to/service-account-key.json (Windows: set FIREBASE_CREDENTIALS_PATH=...).
For queries: Create a composite index on transactions collection (address ASC, timestamp DESC) via the console (link auto-generated on first error).


Notifications (Optional):

In services/notification_service.py, update self.email and self.password with your Gmail and app password (generate at myaccount.google.com/apppasswords).
Update user_email to a recipient address.


Run the App:
textstreamlit run app.py
Open http://localhost:8501.

Usage

Wallet Setup: Generate or import a 12-word mnemonic. Address derives automatically—view on "Balance & Send".
Send ETH/USD:

Enter recipient (e.g., 0x742d35Cc6634C0532925a3b8D4C9db96c728b0b4).
Choose ETH/USD amount.
"Get Quote & Prepare" (creates expiry message).
"Confirm & Sign" (signs with private key; backend verifies).


View History: Switch to "Transaction History" for logs.
Notifications: Emails sent on success (check spam).

Security Notes: Mnemonics stored in session state (in-memory). For prod, use encrypted storage/hardware wallets.
File Structure
textmock_web3_wallet/
├── app.py                 # Main Streamlit app
├── services/              # Backend modules
│   ├── __init__.py
│   ├── wallet_manager.py  # Mnemonic/wallet derivation & signing
│   ├── database_manager.py # Firestore CRUD
│   ├── transaction_service.py # Transfer logic & API
│   └── notification_service.py # Email notifications
├── requirements.txt       # Dependencies
├── documentation.txt      # Detailed internal docs
└── README.md              # This file
Troubleshooting

Import Errors: Reinstall deps: pip install -r requirements.txt --upgrade.
Firebase Init: Check env var and JSON path.
Signing/Verification: Ensure eth-account version matches (0.9.0 for str addresses).
Firestore Index: Create via console link on query error.
Gmail Auth: Use app password, not regular one.
Session Loss: Re-import mnemonic after refresh.
