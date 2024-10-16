from logic.mongodb_database import bank_assets,users_collection,bank_collection,bank_assets_record
from datetime import datetime,timedelta

def fd(username, amount):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return
    current_worth = user.get('worth', 0)
    fd_amount = int(amount)
    current_fd_amount = user.get('fd', 0)
    if current_worth<fd_amount:
        return
    new_fd_amount = current_fd_amount + fd_amount
    bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})
    bank_assets=bank_assets_record.get('total_assets',0)
    new_bank_assets=bank_assets+fd_amount
    new_worth = current_worth - fd_amount
    users_collection.update_one(
        {'user_name': username},
        {
            '$set': {
                'worth': new_worth,
                'fd': new_fd_amount
            }
        }
    )
    bank_collection.update_one({'_id': 'bank_assets'}, {'$set': {'total_assets': new_bank_assets}})
