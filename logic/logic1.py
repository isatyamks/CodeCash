from datetime import datetime, timedelta
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client.login
users_collection = db.users

def update_worth(username, amount, action):
    user = users_collection.find_one({'user_name': username})
    if user:
        current_worth = user.get('worth', 0)
        if action == 'deposit':
            if current_worth>=amount:
                new_worth = current_worth - amount
            else:
                new_worth=current_worth  # Adjust for deposit
        elif action == 'loan':
            new_worth = current_worth + amount  # Adjust for loan
        else:
            new_worth = current_worth  # Default action (like next month)

        users_collection.update_one({'user_name': username}, {'$set': {'worth': new_worth}})

def move_to_next_month(username, income, expenditure):
    user = users_collection.find_one({'user_name': username})
    if user:
        current_worth = user.get('worth', 0)
        net_gain = income - expenditure
        new_worth = current_worth + net_gain

        users_collection.update_one({'user_name': username}, {'$set': {'worth': new_worth}})

        # Update current date to next month
        current_date = user.get('current_date', datetime.now())
        new_date = current_date + timedelta(days=30)  # Assuming a month is 30 days
        users_collection.update_one({'user_name': username}, {'$set': {'current_date': new_date}})
