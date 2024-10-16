from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

# import logic
import logic.logic1 as logic
from forms.forms import LoginForm, SignInForm

app = Flask(__name__)

# Changed the app.secret_key = 'Ifsfss584' to app.config['SECRET_KEY'] = 'Ifsfss584'
# It follows the best practice amongst flask devs, and it's also extensible.
app.config['SECRET_KEY'] = 'Ifsfss584'
client = MongoClient('mongodb://localhost:27017')

# client database
db = client.login
users_collection = db.users

# bank data mongodb datasets
db_codecash = client.bank
bank_collection = db_codecash['assets']


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# ---------------------------------------------------------------------------------------


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # This gets the value of each field from the frontend
        email = form.email.data
        password = form.password.data
        user = users_collection.find_one({'email': email})

        if user and user['password'] == password:
            session['user'] = user['user_name']  # this was the main game----------->
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
        worth = 0

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
            'worth': worth
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

    print(current_date)
    print(month_year)
    return render_template('index.html', month_year=month_year, username=username, worth=worth, bank=bank_money)


@app.route('/home')
# @login_required
def home():
    username = session.get('user')
    user = users_collection.find_one({'user_name': username})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    worth = user.get('worth', 0)
    print(month_year)
    asset_document = bank_collection.find_one({'_id': 'bank_assets'})
    bank_money = asset_document.get('total_assets')
    return render_template('index.html', month_year=month_year, username=username, worth=worth, bank=bank_money)


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
        user = users_collection.find_one({'username': username})
        if user:
            amount = request


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
                logic.loan(username, amount, time_period)

    # Fetch the updated user data
    user = users_collection.find_one({'user_name': username})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    worth = user.get('worth', 0)
    fd = user.get('fd', 0)
    loan = user.get('loan', 0)
    asset_document = bank_collection.find_one({'_id': 'bank_assets'})
    bank_money = asset_document.get('total_assets') if asset_document else 0
    return render_template('bank.html', month_year=month_year, username=username, worth=worth, fd=fd, loan=loan,
                           bank=bank_money)


@app.route('/leaderboard')
@login_required
def leaderboard():
    users = users_collection.find()
    username = session.get('user')
    user = users_collection.find_one({'user_name': username})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    worth = user.get('worth', 0)
    asset_document = bank_collection.find_one({'_id': 'bank_assets'})
    bank_money = asset_document.get('total_assets')
    return render_template('leaderboard.html', users=users, user=user, username=username, month_year=month_year,
                           worth=worth, bank=bank_money)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    username = session.get('user')
    user = users_collection.find_one({'user_name': username})

    if not user:
        flash('User not found.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_info':
            new_email = request.form.get('email')
            current_password = request.form.get('current_password')
            new_password = request.form.get('password')
            if not check_password_hash(user['password'], current_password):
                last_changed_date = user.get('password_last_changed', None)
                if last_changed_date:
                    flash(
                        f'Incorrect password. Your password was last changed on {last_changed_date.strftime("%B %d, %Y")}.')
                else:
                    flash('Incorrect password.')
                return redirect(url_for('settings'))

            if check_password_hash(user['password'], new_password):
                flash('New password cannot be the same as the current password.')
                return redirect(url_for('settings'))

            updates = {}
            if new_email and new_email != user['email']:
                if users_collection.find_one({'email': new_email}):
                    flash('Email already exists.')
                else:
                    updates['email'] = new_email

            if new_password:
                updates['password'] = generate_password_hash(new_password)
                updates['password_last_changed'] = datetime.now()

            if updates:
                users_collection.update_one({'user_name': username}, {'$set': updates})
                flash('Information updated successfully.')

        elif action == 'delete_account':
            password = request.form.get('password')

            if check_password_hash(user['password'], password):
                users_collection.delete_one({'user_name': username})
                session.clear()
                flash('Account deleted successfully.')
                return redirect(url_for('login'))
            else:
                last_changed_date = user.get('password_last_changed', None)
                if last_changed_date:
                    flash(
                        f'Incorrect password. Your password was last changed on {last_changed_date.strftime("%B %d, %Y")}.')
                else:
                    flash('Incorrect password.')
                return redirect(url_for('settings'))

        elif action == 'logout':
            session.clear()
            flash('Logged out successfully.')
            return redirect(url_for('login'))

    return render_template('settings.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
