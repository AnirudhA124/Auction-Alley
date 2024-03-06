from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Dummy user data for demonstration
users = {'admin': 'admin'}

# Define the products with scheduled time
products = [
    {"name": "Product 1", "description": "Description of product 1", "starting_bid": 50, "scheduled_time": "2024-03-07T22:00:00"},
    {"name": "Product 2", "description": "Description of product 2", "starting_bid": 100, "scheduled_time": "2024-03-07T22:30:00"},
    {"name": "Product 3", "description": "Description of product 3", "starting_bid": 75, "scheduled_time": "2024-03-06T22:00:00"},
    {"name": "Product 4", "description": "Description of product 4", "starting_bid": 75, "scheduled_time": "2024-03-06T22:00:00"},
]

# Filter out expired auctions
current_time = datetime.now()
upcoming_products = [product for product in products if datetime.fromisoformat(product["scheduled_time"]) > current_time]

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
        print("Password/username incorrect!!")
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
    # Render dashboard template with upcoming auctions
    return render_template('main.html', products=upcoming_products)

if __name__ == '__main__':
    app.run(debug=True)
