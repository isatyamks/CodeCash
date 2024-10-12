from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session  # Make sure flash is imported
from pymongo import MongoClient
from datetime import datetime

import logic.logic1 as logic
from forms.forms import LoginForm, SignInForm

app = Flask(__name__)

# Changed the app.secret_key = 'Ifsfss584' to app.config['SECRET_KEY'] = 'Ifsfss584'
# It follows the best practice amongst flask devs, and it's also extensible.
app.config['SECRET_KEY'] = 'Ifsfss584'
client = MongoClient('mongodb://localhost:27017')


# Client database
db = client.login
users_collection = db.users

# Bank data MongoDB datasets
db_codecash = client.bank
bank_collection = db_codecash['assets']


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # This gets the value of each field from the frontend
        email = form.email.data
        password = form.password.data
        user = users_collection.find_one({'email': email})

        if user and user['password'] == password:
            session['user'] = user['user_name']
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')  # Flash a message if login is incorrect

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignInForm()
    if form.validate_on_submit():
        # This gets the value of each field from the frontend
        user_name = form.user_name.data
        email = form.email.data
        password = form.password.data
        signup_time = datetime.now()

        # Check if email already exists
        if users_collection.find_one({'email': email}):
            flash('Email already exists')
            return redirect(url_for('signup'))

        # Check if username already exists
        if users_collection.find_one({'user_name': user_name}):
            flash('Username already exists')
            return redirect(url_for('signup'))

        # Insert new user
        users_collection.insert_one({
            'user_name': user_name,
            'email': email,
            'password': password,
            'signup_time': signup_time,
            'worth': 0
        })
        session['user'] = user_name
        return redirect(url_for('index'))

    return render_template('signup.html', form=form)


@app.route('/')
@login_required
def index():
    username = session.get('user')
    user = users_collection.find_one({'user_name': username})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    worth = user.get('worth', 0)

    asset_document = bank_collection.find_one({'_id': 'bank_assets'})
    bank_money = asset_document.get('total_assets') if asset_document else 0

    return render_template('index.html', month_year=month_year, username=username, worth=worth, bank=bank_money)


@app.route('/home')
@login_required
def home():
    return index()


@app.route('/next_month', methods=['POST'])
@login_required
def next_month():
    username = session.get('user')
    if username:
        logic.next_month(username)
    return redirect(url_for('index'))


@app.route('/stock', methods=['GET', 'POST'])
@login_required
def stock():
    username = session.get('user')
    if request.method == 'POST':
        user = users_collection.find_one({'user_name': username})
        if user:
            # Implement your stock buying logic here
            pass


@app.route('/bank', methods=['GET', 'POST'])
@login_required
def bank():
    username = session.get('user')
    if request.method == 'POST':
        amount = request.form.get('amount')
        time_period = request.form.get('time-period')
        action_type = request.form.get('action-type')
        logic.process_bank_action(username, action_type, amount, time_period)

    user = users_collection.find_one({'user_name': username})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    worth = user.get('worth', 0)
    fd = user.get('fd', 0)
    loan = user.get('loan', 0)
    bank_money = bank_collection.find_one({'_id': 'bank_assets'}).get('total_assets', 0)

    return render_template('bank.html', month_year=month_year, username=username, worth=worth, fd=fd, loan=loan,
                           bank=bank_money)


@app.route('/leaderboard')
@login_required
def leaderboard():
    users = list(users_collection.find())
    user = users_collection.find_one({'user_name': session.get('user')})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    worth = user.get('worth', 0)
    bank_money = bank_collection.find_one({'_id': 'bank_assets'}).get('total_assets', 0)

    return render_template('leaderboard.html', users=users, user=user, username=session.get('user'),
                           month_year=month_year, worth=worth, bank=bank_money)


if __name__ == '__main__':
    app.run(debug=True)
