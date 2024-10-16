from logic.mongodb_database import bank_assets,users_collection,bank_collection,bank_assets_record
from datetime import datetime,timedelta



def next_month(username):
    income = 600
    expenditure = 500
    user = users_collection.find_one({'user_name': username})
    bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})
    bank_assets=bank_assets_record.get('total_assets',0)
    if not user:
        return
    
    current_worth = user.get('worth', 0)
    fd_amount = user.get('fd', 0)
    loan_amount = user.get('loan', 0)
    loan_time = user.get('loan_time', 0)
    loan_time = int(loan_time)
    new_bank_assets=bank_assets
    new_worth = current_worth  
    new_loan_amount = loan_amount  
    new_worth = current_worth + income - expenditure
    if loan_amount > 0:
        if loan_time > 0:
            
            
            
            loan_time -= 1
        else:
            
            new_worth -= loan_amount * 0.1
            new_bank_assets +=bank_assets*0.1
            new_loan_amount = loan_amount - loan_amount * 0.1
    
    new_worth += fd_amount * 0.05
    new_bank_assets -= fd_amount *0.05
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
