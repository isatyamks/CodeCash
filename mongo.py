from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management and flash messages

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.your_database_name
users_collection = db.users

@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
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
        
        existing_user = users_collection.find_one({'email': email})
        
        if existing_user:
            flash('Email already exists')
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            users_collection.insert_one({
                'name': name,
                'email': email,
                'password': hashed_password
            })
            session['user'] = name
            return redirect(url_for('index'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
