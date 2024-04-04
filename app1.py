from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import cx_Oracle
import pickle
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy user data for demonstration
users = {'admin': 'admin'}

# Define the products with scheduled time
products = [
    {"name": "Product 1", "description": "Description of product 1", "starting_bid": 50, "scheduled_time": "2024-04-07T22:00:00"},
    {"name": "Product 2", "description": "Description of product 2", "starting_bid": 100, "scheduled_time": "2024-04-07T22:30:00"},
    {"name": "Product 3", "description": "Description of product 3", "starting_bid": 75, "scheduled_time": "2024-04-06T22:00:00"},
    {"name": "Product 4", "description": "Description of product 4", "starting_bid": 75, "scheduled_time": "2024-04-06T22:00:00"},
]

item = {
        'title': 'Telephone',
        'photo': './static/img2.jpg',
        'description': 'This is a description of the example item.'
    }

# Filter out expired auctions
current_time =datetime.now()
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
    if check_seller_credentials(username,password):
        # Redirect to the dashboard or home page upon successful login
        cursor.execute("SELECT seller_id FROM seller WHERE email = :email", {'email': username})
        seller_id = cursor.fetchone()[0]
        session['seller_id'] = seller_id
        return render_template('main_seller.html', products=upcoming_products)
    elif check_buyer_credentials(username,password):
        cursor.execute("SELECT buyer_id FROM buyer WHERE email = :email", {'email': username})
        buyer_id = cursor.fetchone()[0]
        session['buyer_id'] = buyer_id
        return render_template('main_buyer.html', products=upcoming_products)
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
    buyer_id = f"buy{unique_id:07d}"
    return buyer_id

def generate_category_id():
    if os.path.exists("category.pkl"):
        with open("category.pkl", "rb") as f:
            try:
                counter = pickle.load(f)
            except EOFError:
                counter = 1
    else:
        counter = 1
    unique_id = counter
    counter += 1
    with open("category.pkl", "wb") as f:
        pickle.dump(counter, f)
    category_id = f"cat{unique_id:07d}"
    return category_id

def generate_bid_id():
    if os.path.exists("bid.pkl"):
        with open("bid.pkl", "rb") as f:
            try:
                counter = pickle.load(f)
            except EOFError:
                counter = 1
    else:
        counter = 1
    unique_id = counter
    counter += 1
    with open("bid.pkl", "wb") as f:
        pickle.dump(counter, f)
    bid_id = f"bid{unique_id:07d}"
    return bid_id

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            # Fetch data from the form
            email = request.form['email']
            password = request.form['password']
            fname = request.form['fname']
            lname = request.form['lname']
            address = request.form['address']
            pincode = int(request.form['pincode'])
            phone_no = int(request.form['phone_no'])
            buyer = 'buyer' in request.form
            seller = 'seller' in request.form

            # Check if email already exists in seller or buyer table
            cursor.execute("SELECT COUNT(*) FROM seller WHERE email = :email", {'email': email})
            seller_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM buyer WHERE email = :email", {'email': email})
            buyer_count = cursor.fetchone()[0]

            if seller_count > 0 and seller:
                # Email already exists in seller table
                flash('Email is already registered as a seller.', 'error')
                return redirect(url_for('signup'))

            if buyer_count > 0 and buyer:
                # Email already exists in buyer table
                flash('Email is already registered as a buyer.', 'error')
                return redirect(url_for('signup'))

            # Execute SQL query to insert seller or buyer information
            if seller:
                seller_id = generate_seller_id()
                cursor.execute("""
                    INSERT INTO seller (seller_id, email, password, fname, lname, address, pincode, phone_no) 
                    VALUES (:seller_id, :email, :password, :fname, :lname, :address, :pincode, :phone_no)
                """, (seller_id, email, password, fname, lname, address, pincode, phone_no))
                connection.commit()
                return render_template('main_seller.html', products=upcoming_products)

            elif buyer:
                buyer_id = generate_buyer_id()
                cursor.execute("""
                    INSERT INTO buyer (buyer_id, email, password, fname, lname, address, pincode, phone_no) 
                    VALUES (:buyer_id, :email, :password, :fname, :lname, :address, :pincode, :phone_no)
                """, (buyer_id, email, password, fname, lname, address, pincode, phone_no))
                connection.commit()
                return render_template('main_buyer.html', products=upcoming_products)

            # Redirect to the dashboard or home page upon successful signup
            return redirect(url_for('dashboard'))

        except Exception as e:
            # Handle any exceptions
            print("Error:", e)
            flash('An error occurred while processing your request.', 'error')
            return redirect(url_for('dashboard'))
    else:
        # Handle GET request (e.g., render the sign-up form)
        return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    # Render dashboard template with upcoming auctions
    return render_template('main.html', products=upcoming_products)

@app.route('/item_display')
def item_display():
    return render_template('item.html')

def generate_item_number():
    if os.path.exists("item.pkl"):
        with open("item.pkl", "rb") as f:
            try:
                counter = pickle.load(f)
            except EOFError:
                counter = 1
    else:
        counter = 1
    unique_id = counter
    counter += 1
    with open("item.pkl", "wb") as f:
        pickle.dump(counter, f)
    item_number = f"ite{unique_id:07d}"
    return item_number

def generate_auction_id():
    if os.path.exists("auction.pkl"):
        with open("auction.pkl", "rb") as f:
            try:
                counter = pickle.load(f)
            except EOFError:
                counter = 1
    else:
        counter = 1
    unique_id = counter
    counter += 1
    with open("auction.pkl", "wb") as f:
        pickle.dump(counter, f)
    auction_id = f"auc{unique_id:07d}"
    return auction_id

@app.route('/bid_display')
def bid_display():
    item = {
        'title': 'Telephone',
        'photo': './static/img2.jpg',
        'description': 'This is a description of the example item.'
    }
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM bid ORDER BY bid_timestamp DESC")
    bids = [{'bidder_id': row[1], 'bid_amount': row[2], 'bid_time': row[3]} for row in cursor.fetchall()]
    cursor.close()
    return render_template('bid.html', item=item, bids=bids)

@app.route('/items', methods=['POST'])
def items():
    if request.method=='POST':
        try:
            if 'seller_id' in session:
                seller_id = session['seller_id']
            else:
                print("No seller!")
            auction_id=generate_auction_id()
            item_number=generate_item_number()
            category_id=generate_category_id()
            title=request.form["title"]
            description=request.form["description"]
            starting_bid=int(request.form["starting_bid"])
            start_time=request.form["start_time"]
            end_time=request.form["end_time"]
            category = request.form['category'].replace('&amp;', 'and')
            start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
            print(auction_id)
            print(seller_id)
            print(item_number)
            print(title)
            print(description)
            print(starting_bid)
            print(start_time)
            print(end_time)
            print(category)
            print(category_id)
            cursor.execute("""
                    INSERT INTO items (item_number, title, description, starting_bid, seller_id) 
                    VALUES (:item_number, :title, :description, :starting_bid, :seller_id)
                """, (item_number,title,description,starting_bid,seller_id))
            connection.commit()
            cursor.execute("""
                    INSERT INTO category (category_id, category_name, item_number) 
                    VALUES (:category_id, :category_name, :item_number)
                """, (category_id,category,item_number))
            connection.commit()
            cursor.execute("""
                    INSERT INTO auction (auction_id, item_number, start_time, end_time,min_bid_amt, seller_id) 
                    VALUES (:auction_id, :item_number, :start_time, :end_time, :min_bid_amt, :seller_id)
                """, (auction_id,item_number,start_time,end_time,starting_bid,seller_id))
            connection.commit()
            print("inserted")
        except Exception as e:
            # Handle any exceptions
            print("Error:", e)
            flash('An error occurred while processing your request.', 'error')
            return render_template('main_seller.html')
    return render_template('main_seller.html')

@app.route('/bid',methods=['POST'])
def bid():
    if request.method=='POST':
        try:
            if 'buyer_id' in session:
                buyer_id = session['buyer_id']
            else:
                print("No buyer!")
            bid_id=generate_bid_id()
            bid_amount = request.form['bid_amount']
            current_time = datetime.now()
            print(bid_id)
            print(bid_amount)
            print(current_time)
            print(buyer_id)
            # Process bid amount here
            return render_template('bid.html', item=item)
        except Exception as e:
            # Handle any exceptions
            print("Error:", e)
            flash('An error occurred while processing your request.', 'error')
            return render_template('main_buyer.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
