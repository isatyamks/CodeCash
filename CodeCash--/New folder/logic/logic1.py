from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb://localhost:27017')
db = client.login
users_collection = db.users
investments_collection = db.investments

def update_worth(username, amount, action):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return

    current_worth = user.get('worth', 0)
    if action == 'deposit':
        new_worth = current_worth + amount
    elif action == 'withdraw' and current_worth >= amount:
        new_worth = current_worth - amount
    else:
        return  # Invalid action or insufficient funds

    users_collection.update_one({'user_name': username}, {'$set': {'worth': new_worth}})







def next_month(username):
    income=1000
    expenditure=500
    user = users_collection.find_one({'user_name': username})
    if not user:
        return
    current_worth = user.get('worth', 0)
    new_worth = current_worth + income - expenditure
    current_date = datetime.now()+timedelta(days=30)
    users_collection.update_one(
        {'user_name': username},
        {
            '$set': {
                'worth': new_worth,
                'current_date':current_date  # Move to next month
            }
        }
    )
    print(current_date)
    








def process_investments(username):
    investments = investments_collection.find({'user_name': username})
    for investment in investments:
        if investment['type'] == 'fd-rd':
            process_fd_rd(username, investment)
        elif investment['type'] == 'mutual-funds':
            process_mutual_funds(username, investment)
        elif investment['type'] == 'bond':
            process_bond(username, investment)

def process_fd_rd(username, investment):
    fd_rd_type = investment['fd_rd_type']
    amount = investment['amount']
    duration = investment['duration']
    start_date = investment['date']
    months_passed = (datetime.now() - start_date).days // 30

    if fd_rd_type == 'fd':
        if months_passed <= duration:
            # Calculate interest based on fixed deposit logic
            interest_rate = 0.05  # Example interest rate per month
            interest = amount * interest_rate
            update_worth(username, interest, 'deposit')
    elif fd_rd_type == 'rd':
        if months_passed < duration:
            # Deduct RD monthly deposit from current worth
            monthly_deposit = amount / duration
            update_worth(username, monthly_deposit, 'withdraw')
            # Calculate interest based on recurring deposit logic
            interest_rate = 0.04  # Example interest rate per month
            interest = amount * interest_rate
            update_worth(username, interest, 'deposit')

def process_mutual_funds(username, investment):
    mutual_funds_type = investment['mutual_funds_type']
    amount = investment['amount']
    duration = investment['duration']
    start_date = investment['date']
    months_passed = (datetime.now() - start_date).days // 30

    if mutual_funds_type == 'sip':
        if months_passed < duration:
            # Deduct SIP monthly investment from current worth
            monthly_investment = amount
            update_worth(username, monthly_investment, 'withdraw')
            # Calculate interest based on SIP logic
            interest_rate = 0.03  # Example interest rate per month
            interest = amount * interest_rate
            update_worth(username, interest, 'deposit')
    elif mutual_funds_type == 'lumpsum':
        if months_passed <= duration:
            # Deduct lumpsum investment upfront from current worth
            update_worth(username, amount, 'withdraw')
            # Calculate interest based on lumpsum logic
            interest_rate = 0.02  # Example interest rate per month
            interest = amount * interest_rate
            update_worth(username, interest, 'deposit')

def process_bond(username, investment):
    amount = investment['amount']
    # Deduct bond investment upfront from current worth
    update_worth(username, amount, 'withdraw')

def invest_in_fd_rd(username, amount, fd_rd_type, duration):
    investments_collection.insert_one({
        'user_name': username,
        'type': 'fd-rd',
        'fd_rd_type': fd_rd_type,
        'amount': amount,
        'duration': duration,
        'date': datetime.now()
    })
    if fd_rd_type == 'fd':
        update_worth(username, amount, 'withdraw')
    print(f"Invested {amount} in {fd_rd_type} for {duration} months.")

def invest_in_mutual_funds(username, amount, mutual_funds_type, duration):
    investments_collection.insert_one({
        'user_name': username,
        'type': 'mutual-funds',
        'mutual_funds_type': mutual_funds_type,
        'amount': amount,
        'duration': duration,
        'date': datetime.now()
    })
    if mutual_funds_type == 'lumpsum':
        update_worth(username, amount, 'withdraw')
    print(f"Invested {amount} in {mutual_funds_type} mutual funds for {duration} months.")

def buy_bond(username, amount, bond_name):
    investments_collection.insert_one({
        'user_name': username,
        'type': 'bond',
        'bond_name': bond_name,
        'amount': amount,
        'date': datetime.now()
    })
    update_worth(username, amount, 'withdraw')
    print(f"Bought bond {bond_name} for {amount}.")

