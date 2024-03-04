from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy user data for demonstration
users = {'user1': 'password1', 'user2': 'password2'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        # Redirect to the dashboard or home page upon successful login
        return redirect(url_for('dashboard'))
    else:
        # You might want to show an error message here
        print("PAssword/username incorrect!!")
        return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    # You can implement signup logic here, such as adding the user to a database
    # For simplicity, I'm just storing it in the users dictionary
    users[username] = password
    # Redirect to the dashboard or home page upon successful signup
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    # Render dashboard template
    return "Welcome to the dashboard!"

if __name__ == '__main__':
    app.run(debug=True)
