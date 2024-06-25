from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from datetime import datetime,timedelta
import logic.logic1 as logic

worth=0

app = Flask(__name__)
app.secret_key = 'Ifsfss584'
client = MongoClient('mongodb://localhost:27017')  
db = client.login
users_collection = db.users



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



@app.route('/')
@login_required
def index():
    username = session.get('user')
    user = users_collection.find_one({'user_name': username})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    purchases_collection = db.purchases
    user_purchases = list(purchases_collection.find({'user_name': username}))
    worth = user.get('worth', 0)  # Fetch the current worth from the database
    print(month_year)
    print(user_purchases)
    return render_template('index.html', month_year=month_year, user_purchases=user_purchases, username=username, worth=worth)

@app.route('/home')
@login_required
def home():
    username = session.get('user')
    user = users_collection.find_one({'user_name': username})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    worth = user.get('worth', 0)  # Fetch the current worth from the database
    print(month_year)
    return render_template('index.html', month_year=month_year, username=username, worth=worth)



@app.route('/next_month', methods=['POST'])
@login_required
def next_month():
    username = session.get('user')
    user = users_collection.find_one({'user_name': username})
    income = 1000  # Example income for next month
    expenditure = 500  # Example expenditure for next month

    if username:
        logic.next_month(username, income, expenditure)
        flash('Moved to the next month! Worth and date updated.')
    
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})

        if user and user['password'] == password:
            session['user'] = user['user_name']
            return redirect(url_for('index'))
        else:
            print('Invalid email or password')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['user_name']
        email = request.form['email']
        password = request.form['password']
        signup_time = datetime.now()

        # Check if email already exists
        existing_email = users_collection.find_one({'email': email})
        if existing_email:
            print('Email already exists')
            return redirect(url_for('signup'))

        # Check if username already exists
        existing_username = users_collection.find_one({'user_name': user_name})
        if existing_username:
            print('Username already exists')
            return redirect(url_for('signup'))

        # If email and username are unique, insert new user
        users_collection.insert_one({
            'user_name': user_name,
            'email': email,
            'password': password,
            'signup_time': signup_time,
            'worth':worth
        })
        session['user'] = user_name
        return redirect(url_for('index'))
    
    return render_template('signup.html')




# Logout route
@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Delete account route



@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        username = session.get('user')  
        if username:
            user = users_collection.find_one({'user_name': username})
            if user:
                email = user['email']  
                result = users_collection.delete_one({'email': email})
                if result.deleted_count > 0:
                    session.pop('user', None)
                    return redirect(url_for('login'))
    return redirect(url_for('settings'))
# Settings route
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')




# @app.route('/bank', methods=['GET', 'POST'])
# def bank():
#     if request.method == 'POST':
#         amount = int(request.form['amount'])
#         action = request.form['action']

#         username = session.get('user')
#         if username:
#             update_worth(username, amount, action)
#             print(f"Updated worth based on {action}.")
        
#     return render_template('bank.html')




@app.route('/bank', methods=['GET', 'POST'])
def bank():
    if request.method == 'GET':
        # Fetch user's information and worth
        username = session.get('user')
        user = users_collection.find_one({'user_name': username})
        if user:
            worth = user.get('worth', 0)
            # Render the bank.html template with user's information
            return render_template('bank.html', username=username, worth=worth, month_year=datetime.now().strftime('%B %Y'))
        else:
            # Handle case where user is not found in database
            return 'User not found'

    elif request.method == 'POST':
        username = session.get('user')
        amount = float(request.form.get('amount', 0))
        action = request.form.get('action')

        if action == 'confirm':
            # Handle different investment types
            investment_type = request.form.get('investment-type')
            
            if investment_type == 'fd-rd':
                fd_rd_type = request.form.get('fd-rd-type')
                duration_fd_rd = int(request.form.get('duration-fd-rd'))
                # Example: investing in FD/RD
                if fd_rd_type in ['fd', 'rd'] and amount > 0 and duration_fd_rd > 0:
                    if fd_rd_type == 'fd':
                        invest_in_fd_rd(username, amount, fd_rd_type, duration_fd_rd)
                    elif fd_rd_type == 'rd':
                        invest_in_fd_rd(username, amount, fd_rd_type, duration_fd_rd)
                    return redirect(url_for('bank'))  # Redirect to bank page after investment

            elif investment_type == 'mutual-funds':
                mutual_funds_type = request.form.get('mutual-funds-type')
                duration_mutual_funds = int(request.form.get('duration-mutual-funds'))
                # Example: investing in Mutual Funds
                if mutual_funds_type in ['lumpsum', 'sip'] and amount > 0 and duration_mutual_funds > 0:
                    invest_in_mutual_funds(username, amount, mutual_funds_type, duration_mutual_funds)
                    return redirect(url_for('bank'))  # Redirect to bank page after investment

            elif investment_type == 'bonds':
                bond_name = request.form.get('bond')
                # Example: buying Bonds
                if bond_name in ['bond1', 'bond2']:  # Adjust as per your bond options
                    amount = 500  # Example amount for bonds
                    buy_bond(username, amount, bond_name)
                    return redirect(url_for('bank'))  # Redirect to bank page after investment

        # If action or investment type is not recognized or form is invalid, redirect to bank page
        return redirect(url_for('bank'))


# Function to process FD/RD investments
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

# Function to process Mutual Funds investments
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

# Function to process Bond purchases
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


@app.route('/market')
@login_required
def market():
    return render_template('market.html')

@app.route('/investment')
@login_required
def investment():
    return render_template('investment.html')

@app.route('/leaderboard')
@login_required
def leaderboard():
    users = users_collection.find()
    return render_template('leaderboard.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
