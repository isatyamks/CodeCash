from datetime import datetime, timedelta
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client.login
users_collection = db.users

def update_worth(username, amount, action):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return

    current_worth = user.get('worth', 0)
    if action == 'loan':
        new_worth = current_worth + amount
    elif action == 'deposit' and current_worth >= amount:
        new_worth = current_worth - amount
    else:
        return  # Invalid action or insufficient funds

    users_collection.update_one({'user_name': username}, {'$set': {'worth': new_worth}})
    print(f"Updated worth based on {action}. New worth: {new_worth}")

def move_to_next_month(username, income, expenditure):
    user = users_collection.find_one({'user_name': username})
    if not user:
        return

    current_worth = user.get('worth', 0)
    new_worth = current_worth + income - expenditure

    # Update the worth and current date
    users_collection.update_one(
        {'user_name': username},
        {
            '$set': {
                'worth': new_worth,
                'current_date': datetime.now() + timedelta(days=30)  # Move to next month
            }
        }
    )
    print(f'Moved to the next month! New worth: {new_worth}')
