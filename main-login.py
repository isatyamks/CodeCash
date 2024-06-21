from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management and flash messages

# In-memory storage for users (for demonstration purposes only)
users = {
    'test@example.com': {
        'name': 'Test User',
        'password': 'password123'  # In a real application, passwords should be hashed
    }
}

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
        user = users.get(email)
        
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
        
        if email in users:
            flash('Email already exists')
        else:
            users[email] = {'name': name, 'password': password}
            session['user'] = name
            return redirect(url_for('index'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
