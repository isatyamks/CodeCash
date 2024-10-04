from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb://localhost:27017')

db_login = client.login
users_collection = db_login.users

db_bank = client.bank
bank_collection = db_bank.assets

# Fetch the bank assets document or initialize if it doesn't exist
bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})

if bank_assets_record is None:
    # Initialize the bank_assets if the document doesn't exist
    bank_collection.insert_one({'_id': 'bank_assets', 'total_assets': 0})
    bank_assets = 0
else:
    bank_assets = int(bank_assets_record.get('total_assets', 0))


def update_worth(username, amount, action):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return "User not found"

    current_worth = user.get('worth', 0)

    if action == 'deposit':
        new_worth = current_worth + amount
        new_bank_assets = bank_assets + amount
    elif action == 'withdraw':
        if current_worth >= amount and bank_assets >= amount:
            new_worth = current_worth - amount
            new_bank_assets = bank_assets - amount
        else:
            return "Insufficient funds"
    else:
        return "Invalid action"

    users_collection.update_one({'user_name': username}, {'$set': {'worth': new_worth}})
    bank_collection.update_one({'_id': 'bank_assets'}, {'$set': {'total_assets': new_bank_assets}})
    return "Transaction successful"
