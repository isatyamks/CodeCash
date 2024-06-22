from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from datetime import datetime,timedelta

worth = 0

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
    print(month_year)
    return render_template('index.html', month_year=month_year)

@app.route('/home')
@login_required
def home():
    username = session.get('user')
    user = users_collection.find_one({'user_name': username})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    print(month_year)
    return render_template('index.html', month_year=month_year)




@app.route('/next_month', methods=['POST'])
@login_required
def next_month():
    income = 850
    expenditure = 400
    net_gain = income - expenditure

    username = session.get('user')
    if username:
        user = users_collection.find_one({'user_name': username})
        if user:
            new_worth = user.get('worth', 0) + net_gain
            users_collection.update_one({'user_name': username}, {'$set': {'worth': new_worth}})
            
            # Update the current date
            current_date = user.get('current_date', datetime.now())
            new_date = current_date + timedelta(days=30)  # Assuming a month is 30 days
            users_collection.update_one({'user_name': username}, {'$set': {'current_date': new_date}})
            
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
            flash('Invalid email or password')
    
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
            flash('Email already exists')
            return redirect(url_for('signup'))

        # Check if username already exists
        existing_username = users_collection.find_one({'user_name': user_name})
        if existing_username:
            flash('Username already exists')
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

@app.route('/bank', methods=['GET', 'POST'])
def bank():
    if request.method == 'POST':
        amount = int(request.form['amount'])
        action = request.form['action']

        if action == 'deposit':
            global worth 
            worth-=amount
            username = session.get('user')  
            if username:
                user = users_collection.find_one({'user_name': username})
                if user:
                    email = user['email']  
                    users_collection.update_one({'email': email}, {'$set': {'worth': worth}})
            print(f"Loan of Rs {amount} approved.")

            
          
        elif action == 'loan':
            
            worth+=amount
            username = session.get('user')  
            if username:
                user = users_collection.find_one({'user_name': username})
                if user:
                    email = user['email']  
                    users_collection.update_one({'email': email}, {'$set': {'worth': worth}})
            print(f"Loan of Rs {amount} approved.")

    return render_template('bank.html')

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
