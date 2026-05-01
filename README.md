# Transparent Donation System

This project contains a Django backend app and a Solidity smart contract for transparent donations.

## Structure

- `blockchain/contracts/Zakat.sol`: Solidity smart contract for donations.
- `blockchain/scripts/deploy.js`: Sample Hardhat deployment script.
- `backend/`: Django backend application.
  - `manage.py`: Django command-line utility.
  - `zakat_project/`: Django project configuration.
  - `zakat_app/`: Django app with models, views, serializers, and blockchain helpers.
- `frontend/templates/`: Django template files.
- `requirements.txt`: Python dependencies.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python backend/manage.py migrate
   ```
4. Create a superuser:
   ```bash
   python backend/manage.py createsuperuser
   ```
5. Start the development server:
   ```bash
   python backend/manage.py runserver
   ```

## Notes

- Update `backend/zakat_project/settings.py` to secure the `SECRET_KEY` and configure production settings.
- Replace placeholder blockchain RPC and transaction logic in `backend/zakat_app/blockchain.py` with real Web3 integration.
