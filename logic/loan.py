from logic.mongodb_database import bank_assets,users_collection,bank_collection,bank_assets_record
from datetime import datetime,timedelta

def loan(username, amount,time_period):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return
    current_worth = user.get('worth', 0)
    loan_amount = int(amount)
    current_loan_amount = user.get('loan', 0)
    new_loan_amount = current_loan_amount + loan_amount
    bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})
    bank_assets=bank_assets_record.get('total_assets',0)
    new_bank_assets=bank_assets-loan_amount
    new_worth = current_worth + loan_amount
    users_collection.update_one(
        {'user_name': username},
        {
            '$set': {
                'worth': new_worth,
                'loan': new_loan_amount,
                'loan_time':time_period
            }
        }
    )
    bank_collection.update_one({'_id': 'bank_assets'}, {'$set': {'total_assets': new_bank_assets}})