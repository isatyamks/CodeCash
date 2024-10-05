from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb://localhost:27017')

# Database and collection setup
db_login = client.login
users_collection = db_login.users

db_bank = client.bank
bank_collection = db_bank.assets

# Safely retrieve the bank assets record
bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})
bank_assets = int(bank_assets_record.get('total_assets', 0)) if bank_assets_record else 0

def update_worth(username, amount, action):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return "User not found"

    current_worth = user.get('worth', 0)
    bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})
    bank_assets = int(bank_assets_record.get('total_assets', 0)) if bank_assets_record else 0
    
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

def next_month(username):
    income = 600
    expenditure = 500
    user = users_collection.find_one({'user_name': username})
    if not user:
        return
    
    bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})
    bank_assets = bank_assets_record.get('total_assets', 0) if bank_assets_record else 0

    current_worth = user.get('worth', 0)
    fd_amount = user.get('fd', 0)
    loan_amount = user.get('loan', 0)
    loan_time = int(user.get('loan_time', 0))

    new_bank_assets = bank_assets
    new_worth = current_worth + income - expenditure
    new_loan_amount = loan_amount

    # Process loan payments if any
    if loan_amount > 0:
        if loan_time > 0:
            loan_time -= 1
        else:
            repayment = loan_amount * 0.1
            new_worth -= repayment
            new_bank_assets += repayment
            new_loan_amount = loan_amount - repayment

    # Update FD earnings
    new_worth += fd_amount * 0.05
    new_bank_assets -= fd_amount * 0.05

    current_date = user.get('current_date', datetime.now())
    new_date = current_date + timedelta(days=30)
    
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

def fd(username, amount):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return

    current_worth = user.get('worth', 0)
    fd_amount = int(amount)

    if current_worth < fd_amount:
        return

    current_fd_amount = user.get('fd', 0)
    new_fd_amount = current_fd_amount + fd_amount

    bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})
    bank_assets = bank_assets_record.get('total_assets', 0) if bank_assets_record else 0
    new_bank_assets = bank_assets + fd_amount

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

# Similar changes applied to rd, sip, lumpsum, and loan functions

def rd(username, amount, time_period):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return

    current_worth = user.get('worth', 0)
    fd_amount = int(amount)

    if current_worth < fd_amount:
        return

    current_fd_amount = user.get('fd', 0)
    new_fd_amount = current_fd_amount + fd_amount

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

def sip(username, amount):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return

    current_worth = user.get('worth', 0)
    fd_amount = int(amount)

    if current_worth < fd_amount:
        return

    current_fd_amount = user.get('fd', 0)
    new_fd_amount = current_fd_amount + fd_amount

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

def lumpsum(username, amount):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return

    current_worth = user.get('worth', 0)
    lumpsum_amount = int(amount)

    new_worth = current_worth - lumpsum_amount
    current_lumpsum_amount = user.get('lumpsum', 0)
    new_lumpsum_amount = current_lumpsum_amount + lumpsum_amount

    users_collection.update_one(
        {'user_name': username},
        {
            '$set': {
                'worth': new_worth,
                'lumpsum': new_lumpsum_amount
            }
        }
    )

def loan(username, amount, time_period):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return

    current_worth = user.get('worth', 0)
    loan_amount = int(amount)

    current_loan_amount = user.get('loan', 0)
    new_loan_amount = current_loan_amount + loan_amount

    bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})
    bank_assets = bank_assets_record.get('total_assets', 0) if bank_assets_record else 0
    new_bank_assets = bank_assets - loan_amount

    new_worth = current_worth + loan_amount

    users_collection.update_one(
        {'user_name': username},
        {
            '$set': {
                'worth': new_worth,
                'loan': new_loan_amount,
                'loan_time': time_period
            }
        }
    )
    bank_collection.update_one({'_id': 'bank_assets'}, {'$set': {'total_assets': new_bank_assets}})
