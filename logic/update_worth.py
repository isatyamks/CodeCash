from logic.mongodb_database import bank_assets,users_collection,bank_collection,bank_assets_record
from datetime import datetime,timedelta


def update_worth(username, amount, action):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return "User not found"

    current_worth = user.get('worth', 0)
    bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})
    bank_assets = int(bank_assets_record.get('total_assets', 0))
    
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

    















