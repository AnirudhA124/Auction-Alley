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
    {"name": "Product 1", "description": "Description of product 1", "starting_bid": 50, "start_time": "2024-04-05T17:10:00", "end_time": "2024-04-05T17:11:00"},
    {"name": "Product 2", "description": "Description of product 2", "starting_bid": 100, "start_time": "2024-04-07T22:30:00", "end_time": "2024-04-07T23:30:00"},
    {"name": "Product 3", "description": "Description of product 3", "starting_bid": 75, "start_time": "2024-04-06T22:00:00", "end_time": "2024-04-06T23:00:00"},
    {"name": "Product 4", "description": "Description of product 4", "starting_bid": 75, "start_time": "2024-04-06T22:00:00", "end_time": "2024-04-06T23:00:00"},
]


item = {
        'title': 'Telephone',
        'photo': './static/img2.jpg',
        'description': 'This is a description of the example item.'
    }

# Filter out expired auctions
current_time =datetime.now()
upcoming_products = [product for product in products if datetime.fromisoformat(product["end_time"]) > current_time]

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
        return redirect(url_for('main_seller'))
    elif check_buyer_credentials(username,password):
        cursor.execute("SELECT buyer_id FROM buyer WHERE email = :email", {'email': username})
        buyer_id = cursor.fetchone()[0]
        session['buyer_id'] = buyer_id
        return redirect(url_for('main_buyer'))
    else:
        # You might want to show an error message here
        print("Password/username incorrect!!")
        return redirect(url_for('index'))

@app.route('/main_seller')
def main_seller():
    try:
        cursor = connection.cursor()

        # Fetch item information from the items and auction tables
        if 'seller_id' in session:
                seller_id = session['seller_id']
        else:
            print("No seller!")  # Using session.get to avoid KeyError if seller_id is not set
        if seller_id:
            # Execute SQL query to fetch item information
            cursor.execute("""
                SELECT i.item_number, i.title, i.description, i.starting_bid, a.start_time, a.end_time
                FROM items i
                JOIN auction a ON i.item_number = a.item_number
                WHERE a.seller_id = :seller_id
            """, {'seller_id': seller_id})

            items = cursor.fetchall()

            # Close the cursor
            cursor.close()
            # Render the main seller template with the fetched items
            # Filter out expired auctions
            current_time = datetime.now()
            upcoming_products = [item for item in items if item[5] > current_time]  # Corrected the indexing for end_time
            print(upcoming_products)
            return render_template('main_seller.html', items=upcoming_products)
        else:
            # Handle the case when seller_id is not set in the session
            flash('Seller ID is not set.', 'error')
            return redirect(url_for('index'))
    except cx_Oracle.DatabaseError as e:
        # Handle Oracle database errors
        print("Database error:", e)
        flash('An error occurred while fetching data.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        # Handle other exceptions
        print("Error:", e)
        flash('An error occurred.', 'error')
        return redirect(url_for('index'))

@app.route('/main_buyer')
def main_buyer():
    try:
        cursor = connection.cursor()

        # Fetch item information from the items and auction tables
        if 'seller_id' in session:
                seller_id = session['seller_id']
        else:
            print("No seller!")  # Using session.get to avoid KeyError if seller_id is not set
        if seller_id:
            # Execute SQL query to fetch item information
            cursor.execute("""
                SELECT i.item_number, i.title, i.description, i.starting_bid, a.start_time, a.end_time
                FROM items i
                JOIN auction a ON i.item_number = a.item_number
                WHERE a.seller_id = :seller_id
            """, {'seller_id': seller_id})

            items = cursor.fetchall()

            # Close the cursor
            cursor.close()
            # Render the main seller template with the fetched items
            # Filter out expired auctions
            current_time = datetime.now()
            upcoming_products = [item for item in items if item[5] > current_time]  # Corrected the indexing for end_time
            print(upcoming_products)
            return render_template('main_buyer.html', items=upcoming_products)
        else:
            # Handle the case when seller_id is not set in the session
            flash('Seller ID is not set.', 'error')
            return redirect(url_for('index'))
    except cx_Oracle.DatabaseError as e:
        # Handle Oracle database errors
        print("Database error:", e)
        flash('An error occurred while fetching data.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        # Handle other exceptions
        print("Error:", e)
        flash('An error occurred.', 'error')
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

            if seller_count > 0 or buyer_count>0 and seller:
                # Email already exists in seller table
                flash('Email is already registered as a seller.', 'error')
                return redirect(url_for('signup'))

            if buyer_count > 0 or seller_count>0 and buyer:
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
                return redirect(url_for('main_seller'))

            elif buyer:
                buyer_id = generate_buyer_id()
                cursor.execute("""
                    INSERT INTO buyer (buyer_id, email, password, fname, lname, address, pincode, phone_no) 
                    VALUES (:buyer_id, :email, :password, :fname, :lname, :address, :pincode, :phone_no)
                """, (buyer_id, email, password, fname, lname, address, pincode, phone_no))
                connection.commit()
                return redirect(url_for('main_buyer'))

        except Exception as e:
            # Handle any exceptions
            print("Error:", e)
            flash('An error occurred while processing your request.', 'error')
            return redirect(url_for('index'))
    else:
        # Handle GET request (e.g., render the sign-up form)
        return render_template('signup.html')

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
    item_number = request.args.get('item_number')
    session['item_number'] = item_number
    cursor = connection.cursor()
    
    # Fetch item details from the database
    cursor.execute("SELECT title, description FROM items WHERE item_number = :item_number", {'item_number': item_number})
    item_row = cursor.fetchone()
    item = {
        'title': item_row[0],
        'photo': './static/img2.jpg',
        'description': item_row[1]
    }
    cursor = connection.cursor()
    sql_query = """SELECT * FROM bid WHERE item_number = :item_number ORDER BY bid_timestamp DESC"""
    cursor.execute(sql_query, {'item_number': item_number})
    bids = [{'bidder_id': row[0], 'bid_amount': row[1], 'bid_time': row[2]} for row in cursor.fetchall()]
    print(bids)
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
            return redirect(url_for('main_seller'))
    return redirect(url_for('main_seller'))

@app.route('/bid', methods=['POST'])
def bid():
    if request.method == 'POST':
        try:
            if 'buyer_id' in session:
                buyer_id = session['buyer_id']
            else:
                print("No buyer!")
            if 'item_number' in session:
                item_number = session['item_number']
            else:
                print("No item number!")
            
            bid_amount = float(request.form['bid_amount'])
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Retrieve previous bid amount
            cursor.execute("SELECT MAX(bid_amount) FROM bid WHERE item_number = :item_number", {'item_number': item_number})
            previous_bid_amount = cursor.fetchone()[0]
            
            # Retrieve starting bid amount
            cursor.execute("SELECT starting_bid FROM items WHERE item_number = :item_number", {'item_number': item_number})
            start_bid = cursor.fetchone()[0]
            
            if bid_amount >= start_bid and (previous_bid_amount is None or bid_amount > previous_bid_amount):
                bid_id = generate_bid_id()
                cursor.execute("""
                        INSERT INTO bid (bid_id, bid_amount, bid_timestamp, buyer_id, item_number) 
                        VALUES (:bid_id, :bid_amount, :bid_timestamp, :buyer_id, :item_number)
                    """, (bid_id, bid_amount, current_time, buyer_id, item_number))
                connection.commit()
                print("Inserted!")
                return redirect(url_for('bid_display', item_number=item_number))
            else:
                print("Bid amount does not meet criteria.")
                flash('Bid amount must be greater than or equal to starting bid and greater than the previous bid.', 'error')
                return redirect(url_for('main_buyer'))
            
        except Exception as e:
            # Handle any exceptions
            print("Error:", e)
            flash('An error occurred while processing your request.', 'error')
            return redirect(url_for('main_buyer'))


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
