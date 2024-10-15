from datetime import datetime, timedelta
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')

# client database
db = client.login
users_collection = db.users

# bank data mongodb datasets
db_codecash = client.bank
bank_collection = db_codecash['assets']
bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})

if bank_assets_record:
    bank_assets = int(bank_assets_record.get('total_assets'))
else:
    bank_assets = 0

def next1_month(username):
    income = 600
    expenditure = 500
    
    # Fetch user and bank assets records
    user = users_collection.find_one({'user_name': username})
    bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})
    
    if not user:
        print(f"User {username} not found.")
        return
    
    if not bank_assets_record:
        print("Bank assets record not found.")
        return
    
    bank_assets = bank_assets_record.get('total_assets', 0)
    
    current_worth = user.get('worth', 0)
    fd_amount = user.get('fd', 0)
    loan_amount = user.get('loan', 0)
    loan_time = int(user.get('loan_time', 0))
    
    new_bank_assets = bank_assets
    new_worth = current_worth + income - expenditure
    new_loan_amount = loan_amount
    
    # Update loan details if there is an outstanding loan
    if loan_amount > 0:
        if loan_time > 0:
            loan_time -= 1
        else:
            new_worth -= loan_amount * 0.1
            new_bank_assets += loan_amount * 0.1
            new_loan_amount -= loan_amount * 0.1
    
    # Update worth with fixed deposit interest
    new_worth += fd_amount * 0.05
    new_bank_assets -= fd_amount * 0.05
    
    # Update the date
    current_date = user.get('current_date', datetime.now())
    new_date = current_date + timedelta(days=30)
    
    # Update user and bank records in the database
    users_collection.update_one(
        {'user_name': username},
        {
            '$set': {
                'worth': new_worth,
                'current_date': new_date,
                'loan': new_loan_amount,
                'loan_time': loan_time
            }
        }
    )
    bank_collection.update_one({'_id': 'bank_assets'}, {'$set': {'total_assets': new_bank_assets}})
    
    print(new_date)
