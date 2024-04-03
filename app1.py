from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import cx_Oracle
import pickle
import os

app = Flask(__name__)

# Dummy user data for demonstration
users = {'admin': 'admin'}

# Define the products with scheduled time
products = [
    {"name": "Product 1", "description": "Description of product 1", "starting_bid": 50, "scheduled_time": "2024-04-07T22:00:00"},
    {"name": "Product 2", "description": "Description of product 2", "starting_bid": 100, "scheduled_time": "2024-04-07T22:30:00"},
    {"name": "Product 3", "description": "Description of product 3", "starting_bid": 75, "scheduled_time": "2024-04-06T22:00:00"},
    {"name": "Product 4", "description": "Description of product 4", "starting_bid": 75, "scheduled_time": "2024-04-06T22:00:00"},
]

# Filter out expired auctions
current_time = datetime.now()
upcoming_products = [product for product in products if datetime.fromisoformat(product["scheduled_time"]) > current_time]

# Database connection
try:
    # Replace 'username', 'password', and 'host:port/service_name' with your actual Oracle connection details
    connection = cx_Oracle.connect('system', '1234', 'localhost:1521/XE')
    cursor = connection.cursor()
except cx_Oracle.DatabaseError as e:
    print("Database connection error:", e)

@app.route('/')
def index():
    return render_template('index.html')

def check_buyer_credentials(email, password):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM buyer WHERE email = :email AND password = :password", {'email': email, 'password': password})
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0

def check_seller_credentials(email, password):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM seller WHERE email = :email AND password = :password", {'email': email, 'password': password})
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if check_buyer_credentials(username,password) or check_seller_credentials(username,password):
        # Redirect to the dashboard or home page upon successful login
        return redirect(url_for('dashboard'))
    else:
        # You might want to show an error message here
        print("Password/username incorrect!!")
        return redirect(url_for('index'))

@app.route('/signup_display', methods=['GET'])
def signup_display():
    return render_template('signup.html')

def generate_seller_id():
    if os.path.exists("seller.pkl"):
        with open("seller.pkl", "rb") as f:
            try:
                counter = pickle.load(f)
            except EOFError:
                counter = 1
    else:
        counter = 1
    unique_id = counter
    counter += 1
    with open("seller.pkl", "wb") as f:
        pickle.dump(counter, f)
    seller_id = f"sel{unique_id:07d}"
    return seller_id

def generate_buyer_id():
    if os.path.exists("buyer.pkl"):
        with open("buyer.pkl", "rb") as f:
            try:
                counter = pickle.load(f)
            except EOFError:
                counter = 1
    else:
        counter = 1
    unique_id = counter
    counter += 1
    with open("buyer.pkl", "wb") as f:
        pickle.dump(counter, f)
    seller_id = f"buy{unique_id:07d}"
    return seller_id

@app.route('/signup', methods=['POST'])
def signup():
    try:
        # Fetch data from the form
        seller_id = generate_seller_id()
        buyer_id=generate_buyer_id()
        email = request.form['email']
        password = request.form['password']
        fname = request.form['fname']
        lname = request.form['lname']
        address = request.form['address']
        pincode = int(request.form['pincode'])
        phone_no = int(request.form['phone_no'])
        buyer = 'buyer' in request.form
        seller = 'seller' in request.form
        print("Seller:",seller)
        print("Buyer:",buyer)
        
        # Execute SQL query to insert seller information
        if seller:
            cursor.execute("""
INSERT INTO seller (seller_id, email, password, fname, lname, address, pincode, phone_no) 
VALUES (:seller_id, :email, :password, :fname, :lname, :address, :pincode, :phone_no)
""", (seller_id, email, password, fname, lname, address, pincode, phone_no))
        
        # Commit the transaction
            connection.commit()
        elif buyer:
            cursor.execute("""
INSERT INTO buyer (buyer_id, email, password, fname, lname, address, pincode, phone_no) 
VALUES (:buyer_id, :email, :password, :fname, :lname, :address, :pincode, :phone_no)
""", (buyer_id, email, password, fname, lname, address, pincode, phone_no))
        
        # Commit the transaction
            connection.commit()
        else:
            print("fuck")
        
        # Redirect to the dashboard or home page upon successful signup
        return redirect(url_for('dashboard'))
    except cx_Oracle.DatabaseError as e:
        # Handle any database errors
        print("Database error:", e)
        return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    # Render dashboard template with upcoming auctions
    return render_template('main.html', products=upcoming_products)

if __name__ == '__main__':
    app.run(debug=True)
