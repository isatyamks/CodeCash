from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'IITbombay4584'
client = MongoClient('mongodb://localhost:27017')  # corrected the port
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
def index():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})

        if user and user['password'] == password:
            session['user'] = user['name']
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        signup_time = datetime.now()

        existing_user = users_collection.find_one({'email': email})
        
        if existing_user:
            flash('Email already exists')
        else:
            users_collection.insert_one({
                'name': name,
                'email': email,
                'password': password,
                'signup_time': signup_time
            })
            session['user'] = name
            return redirect(url_for('index'))
    
    return render_template('signup.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/bank')
@login_required
def bank():
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
    return render_template('leaderboard.html')



if __name__ == '__main__':
    app.run(debug=True)
