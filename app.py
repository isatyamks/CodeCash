from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session  
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from datetime import datetime
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError


from logic import fd,rd,loan,lumpsum,update_month,update_worth


app = Flask(__name__)
app.secret_key = 'Ifsfss584'
client = MongoClient('mongodb://localhost:27017')

# CSRF protection
csrf = CSRFProtect(app)

# Client database
db = client.login
users_collection = db.users

# Bank data MongoDB datasets
db_codecash = client.bank
bank_collection = db_codecash['assets']

# csrf error handling
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            session['user'] = user['user_name']
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')  # Flash a message if login is incorrect

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['user_name']
        email = request.form['email']
        password = request.form['password']
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
            'password': generate_password_hash(password),
            'signup_time': signup_time,
            'worth': 0,
            'password_last_changed': signup_time  # Store password change time
        })
        session['user'] = user_name
        return redirect(url_for('index'))

    return render_template('signup.html')

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
        update_month.next_month(username)
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

    return render_template('bank.html', month_year=month_year, username=username, worth=worth, fd=fd, loan=loan, bank=bank_money)

@app.route('/leaderboard')
@login_required
def leaderboard():
    users = list(users_collection.find())
    user = users_collection.find_one({'user_name': session.get('user')})
    current_date = user.get('current_date', datetime.now())
    month_year = current_date.strftime("%B-%Y")
    worth = user.get('worth', 0)
    bank_money = bank_collection.find_one({'_id': 'bank_assets'}).get('total_assets', 0)

    return render_template('leaderboard.html', users=users, user=user, username=session.get('user'), month_year=month_year, worth=worth, bank=bank_money)

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
                    flash(f'Incorrect password. Your password was last changed on {last_changed_date.strftime("%B %d, %Y")}.')
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
                    flash(f'Incorrect password. Your password was last changed on {last_changed_date.strftime("%B %d, %Y")}.')
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
