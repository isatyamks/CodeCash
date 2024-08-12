from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from datetime import datetime,timedelta
import logic.logic1 as logic

worth =0

app = Flask(__name__)
app.secret_key = 'Ifsfss584'
client = MongoClient('mongodb://localhost:27017')  


#client database

db = client.login
users_collection = db.users

#bank data mongodb datasets
db_codecash = client.bank
bank_collection = db_codecash['assets']




def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
#---------------------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})

        if user and user['password'] == password:
            session['user'] = user['user_name']    #this was the main game----------->
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
#---------------------------------------------------------------------------------------


@app.route('/')
@login_required
def index():

    
    username = session.get('user')
    user = users_collection.find_one({'user_name': username})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    
    worth = user.get('worth', 0)  

    asset_document = bank_collection.find_one({'_id': 'bank_assets'})
    bank_money = asset_document.get('total_assets') 
    

    print(current_date)
    print( month_year)
    return render_template('index.html', month_year=month_year,username=username, worth=worth,bank=bank_money)


@app.route('/home')
@login_required
def home():
    username = session.get('user')
    user = users_collection.find_one({'user_name': username})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    worth = user.get('worth', 0)  
    print(month_year)
    asset_document = bank_collection.find_one({'_id': 'bank_assets'})
    bank_money = asset_document.get('total_assets') 
    return render_template('index.html', month_year=month_year,username=username, worth=worth,bank=bank_money)


@app.route('/next_month', methods=['POST'])
@login_required
def next_month():
    username = session.get('user')
    if username:
        logic.next_month(username)
    return redirect(url_for('index'))


@app.route('/bank', methods=['GET', 'POST'])
@login_required
def bank():
    username = session.get('user')
    if request.method == 'POST':
        user = users_collection.find_one({'user_name': username})
        if user:
            amount = request.form.get('amount')
            time_period = request.form.get('time-period')
            action_type = request.form.get('action-type')
            print("action=", action_type, "time_period", time_period, "amount", amount)
            if action_type == 'fd':
                logic.fd(username, amount)
            elif action_type == 'rd':
                logic.rd(username, amount, time_period)
            elif action_type == 'sip':
                logic.sip(username, amount)
            elif action_type == 'lumpsum':
                logic.lumpsum(username, amount)
            elif action_type == 'loan':
                logic.loan(username,amount,time_period)

    # Fetch the updated user data
    user = users_collection.find_one({'user_name': username})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    worth = user.get('worth', 0)
    fd = user.get('fd',0)
    loan =user.get('loan',0)

    return render_template('bank.html', month_year=month_year, username=username, worth=worth,fd=fd,loan=loan,bank=logic.bank_assets)


@app.route('/leaderboard')
@login_required
def leaderboard():
    users = users_collection.find()
    username = session.get('user')
    user = users_collection.find_one({'user_name': username})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    worth = user.get('worth', 0)  
    return render_template('leaderboard.html', users=users,user=user,username=username,month_year=month_year,worth=worth,bank=logic.bank_assets)


    
if __name__ == '__main__':
    app.run(debug=True)







from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'Ifsfss584'

# Initialize MongoDB client
client = MongoClient('mongodb://localhost:27017')

# Access the 'bank' collection within the 'codecash' database

@app.route('/get_total_assets', methods=['GET'])
def get_total_assets():
    # Fetch the document with the _id 'bank_assets'
    # Print the total_assets value to the console
    print(f"Total Assets: {total_assets}")
    
    # Return the total_assets as a JSON response
    return jsonify({'total_assets': total_assets})

if __name__ == '__main__':
    app.run(debug=True)
