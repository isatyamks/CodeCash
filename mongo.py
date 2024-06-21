from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from datetime import datetime













app = Flask(__name__)
app.secret_key = 'IITbombay4584'
client = MongoClient('mongodb://localhost:27017')
db = client.login
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



























if __name__ == '__main__':
    app.run(debug=True)
