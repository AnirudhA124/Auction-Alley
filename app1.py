from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import cx_Oracle
import pickle
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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

def check_admin_credentials(email, password):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM admin WHERE email_id = :email_id AND password = :password", {'email_id': email, 'password': password})
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
    elif check_admin_credentials(username,password):
        cursor.execute("SELECT admin_id FROM admin WHERE email_id = :email_id", {'email_id': username})
        admin_id = cursor.fetchone()[0]
        session['admin_id'] = admin_id
        return redirect(url_for('admin_dashboard'))
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

def generate_payment_id():
    if os.path.exists("payment.pkl"):
        with open("payment.pkl", "rb") as f:
            try:
                counter = pickle.load(f)
            except EOFError:
                counter = 1
    else:
        counter = 1
    unique_id = counter
    counter += 1
    with open("payment.pkl", "wb") as f:
        pickle.dump(counter, f)
    payment_id = f"pay{unique_id:07d}"
    return payment_id


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
        'photo': f'./static/{item_number}.jpg',
        'description': item_row[1]
    }
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(bid_amount) FROM bid WHERE item_number = :item_number", {'item_number': item_number})
    max_bid_amount = cursor.fetchone()[0]
    
    # Update the auction table's final_amt field with the maximum bid amount
    cursor.execute("UPDATE auction SET final_amt = :max_bid_amount WHERE item_number = :item_number", {'max_bid_amount': max_bid_amount, 'item_number': item_number})
    connection.commit()  # Commit the transaction
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
            if 'image' in request.files:
                image = request.files['image']
                image.save(f'static/{item_number}.jpg')
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
                    INSERT INTO auction_seller (auction_id, seller_id) 
                    VALUES (:auction_id, :seller_id)
                """, (auction_id,seller_id))
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

@app.route('/auction_history', methods=['GET'])
def auction_history():
    try:
        cursor = connection.cursor()
        if 'seller_id' in session:
            seller_id = session['seller_id']
            print(seller_id)
        else:
            print("No seller!")
            # Redirect if seller_id is not set in session
            flash('Seller ID is not set.', 'error')
            return redirect(url_for('main_seller'))
        
        if seller_id:
            # Execute SQL query to fetch item information
            cursor.execute("""
        SELECT title, description, final_amt, start_time, end_time, items.item_number
        FROM items
        JOIN auction ON items.item_number = auction.item_number
        WHERE auction.seller_id = :seller_id
    """, {'seller_id': seller_id})

            auction_items = cursor.fetchall()
            print(auction_items)
            cursor.close()
            return render_template('auction_history.html', auction_items=auction_items)
        else:
            # Handle the case when seller_id is not set in the session
            flash('Seller ID is not set.', 'error')
            return redirect(url_for('main_seller'))
    except cx_Oracle.DatabaseError as e:
        # Handle Oracle database errors
        print("Database error:", e)
        flash('An error occurred while fetching data.', 'error')
        return redirect(url_for('main_seller'))
    except Exception as e:
        # Handle other exceptions
        print("Error:", e)
        flash('An error occurred.', 'error')
        return redirect(url_for('main_seller'))
    
@app.route('/bid_history', methods=['GET'])
def bid_history():
    result_set = cursor.var(cx_Oracle.CURSOR)
    cursor.execute("BEGIN :result := get_bid_info(:buyer_id); END;",
               result=result_set,
               buyer_id='buy0000001')
    rows = result_set.getvalue().fetchall()
    print(rows)
    return render_template('bid_history.html',bids=rows)

@app.route('/purchase_history',methods=['GET'])
def purchase_history():
    if 'buyer_id' in session:
        buyer_id = session['buyer_id']
        try:
            # Establish database connection
            cursor = connection.cursor()

            # Define the SQL query
            sql_query = """
            select item_number,title,final_amt from items natural join auction where auction_id in (select auction_id from auction_buyer where buyer_id= :buyer_id)
            """

            # Execute the SQL query with parameter
            cursor.execute(sql_query, {'buyer_id': buyer_id})

            # Fetch all rows from the result set
            rows = cursor.fetchall()

            # Close cursor and connection
            cursor.close()
            connection.close()

            # Render the template with the data
            return render_template('purchase_history.html', items=rows)

        except cx_Oracle.Error as e:
            error_message = f"Database error: {e}"
            print(error_message)
            return "Error"

    else:
        return "No buyer_id in session"

@app.route('/bids_won',methods=['GET'])
def bids_won():
    if 'buyer_id' in session:
                buyer_id = session['buyer_id']
                print(buyer_id)
    else:
        print("No buyer!")
    cursor = connection.cursor()

    # Define the SQL query
    sql_query = """
        UPDATE bid b1
        SET bid_status = 'success'
        WHERE EXISTS (
            SELECT 1
            FROM auction a
            WHERE a.end_time < CURRENT_TIMESTAMP
        )
        AND bid_amount = (
            SELECT MAX(bid_amount)
            FROM bid b2
            WHERE b1.item_number = b2.item_number
            GROUP BY b2.item_number
            HAVING b1.item_number = b2.item_number
        )
    """

    # Execute the SQL query
    cursor.execute(sql_query)

    # Commit the transaction
    connection.commit()
    sql_query = """
        SELECT title, items.item_number, bid_amount
        FROM items
        JOIN bid ON items.item_number = bid.item_number
        WHERE bid.bid_status = 'success'
        AND bid.buyer_id = :buyer_id
    """

    # Commit the transaction
    connection.commit()

    # Execute the SQL query with the buyer_id input
    cursor.execute(sql_query, {'buyer_id': buyer_id})

    # Fetch all rows
    rows = cursor.fetchall()
    cnt=0
    for i in rows:
        cnt=cnt+1
    item_number=rows[cnt-1][1]
    print(item_number)
    sql_query = """
    SELECT auction_id 
    FROM auction 
    JOIN bid ON auction.item_number = bid.item_number 
    WHERE bid_status ='success' 
    AND bid.buyer_id=:buyer_id
    AND auction.item_number=:item_number
"""

    # Execute the SQL query with the provided inputs
    cursor.execute(sql_query, {'buyer_id': buyer_id, 'item_number': item_number})

    # Fetch all the rows
    auction_id = cursor.fetchall()[0][0]
    print(auction_id)
    print(rows)
    return render_template('bids_won.html',items=rows,auction_id=auction_id)

@app.route('/payment',methods=['GET'])
def payment():
    auction_id = request.args.get('auction_id')
    print(auction_id)
    # session['auction_id_payment']=auction_id
    payment_id=generate_payment_id()
    if 'buyer_id' in session:
        buyer_id = session['buyer_id']
        print(buyer_id)
    else:
        print("No buyer!")
    # if 'auction_id_payment' in session:
    #     auction_id = session['auction_id_payment']
    #     print(auction_id)
    # else:
    #     print("No auction_id!")
    cursor = connection.cursor()
    sql_query = """
        SELECT seller_id, final_amt
        FROM auction
        WHERE auction_id = :auction_id
    """
    cursor.execute(sql_query, {'auction_id': auction_id})
    result = cursor.fetchone()
    if result:
        seller_id, final_amt = result
    cursor.execute("""
                INSERT INTO auction_buyer (auction_id, buyer_id) 
                VALUES (:auction_id, :buyer_id)
            """, (auction_id,buyer_id))
    connection.commit()
    cursor.execute("""
                INSERT INTO payment (payment_id, final_amt,seller_id,buyer_id) 
                VALUES (:payment_id, :final_amt, :seller_id, :buyer_id)
            """, (payment_id,final_amt,seller_id,buyer_id))
    connection.commit()
    return render_template('payment.html')

@app.route('/payment_done',methods=['GET','POST'])
def payment_done():
    return render_template('purchase_history.html')

@app.route('/admin_dashboard',methods=['GET'])
def admin_dashboard():
    cursor = connection.cursor()

    # Define the SQL query
    sql_query = """
        SELECT category_name, COUNT(category_id)
        FROM category
        GROUP BY category_name
    """

    # Execute the SQL query
    cursor.execute(sql_query)

    # Fetch all rows from the result set
    rows = cursor.fetchall()
    print(rows)
    buyer_cnt_query="""select count(buyer_id) from buyer
    """
    cursor.execute(buyer_cnt_query)
    buyer_count=cursor.fetchone()[0]
    seller_cnt_query="""select count(buyer_id) from buyer
    """
    cursor.execute(seller_cnt_query)
    seller_count=cursor.fetchone()[0]
    return render_template('admin_dashboard.html',items=rows,buyer_count=buyer_count,seller_count=seller_count)

@app.route('/delete_buyer_display',methods=['GET'])
def delete_buyer_display():
    return render_template('admin_deleteBuyer.html')

@app.route('/delete_seller_display',methods=['GET'])
def delete_seller_display():
    return render_template('admin_deleteSeller.html')

@app.route('/delete_buyer',methods=['GET','POST'])
def delete_buyer():
    if request.method=='POST':
        buyer_id=request.form['buyer_id']
        cursor = connection.cursor()

        # Define the input parameters
        p_buyer_id = buyer_id # Replace 'your_seller_id' with the seller ID you want to delete
        p_result = cursor.var(cx_Oracle.STRING)

        # Call the PL/SQL procedure
        cursor.callproc("delete_buyer", [p_buyer_id, p_result])

        # Print the result
        print(p_result.getvalue())

        # Commit the transaction
        connection.commit()

    return render_template('admin_dashboard.html')

@app.route('/delete_seller',methods=['GET','POST'])
def delete_seller():
    if request.method=='POST':
        seller_id=request.form['seller_id']
        cursor = connection.cursor()

        # Define the input parameters
        p_seller_id = seller_id # Replace 'your_seller_id' with the seller ID you want to delete
        p_result = cursor.var(cx_Oracle.STRING)

        # Call the PL/SQL procedure
        cursor.callproc("delete_seller", [p_seller_id, p_result])

        # Print the result
        print(p_result.getvalue())

        # Commit the transaction
        connection.commit()

    return render_template('admin_dashboard.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
