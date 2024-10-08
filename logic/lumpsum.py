from logic.mongodb_database import bank_assets,users_collection,bank_collection,bank_assets_record
from datetime import datetime,timedelta

def lumpsum(username, amount):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return
    current_worth = user.get('worth', 0)
    lumpsum_amount = int(amount)
    current_lumpsum_amount = user.get('fd', 0)
    new_lumpsum_amount = current_lumpsum_amount + lumpsum_amount
    new_worth = current_worth - lumpsum_amount
    users_collection.update_one(
        {'user_name': username},
        {
            '$set': {
                'worth': new_worth,
                'lumpsum': new_lumpsum_amount
            }
        }
    )