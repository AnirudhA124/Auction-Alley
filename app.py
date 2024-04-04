from flask import Flask, render_template, request
import cx_Oracle
import datetime

app = Flask(__name__)

# Connect to Oracle database
connection = cx_Oracle.connect('system', '1234', 'localhost:1521/XE')

@app.route('/')
def index():
    item = {
        'title': 'Telephone',
        'photo': './static/img2.jpg',
        'description': 'This is a description of the example item.'
    }
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM bids ORDER BY bid_time DESC")
    bids = [{'bidder_id': row[1], 'bid_amount': row[2], 'bid_time': row[3]} for row in cursor.fetchall()]
    cursor.close()
    return render_template('bid.html', item=item, bids=bids)

@app.route('/bid', methods=['POST'])
def submit_bid():
    if request.method == 'POST':
        bid_amount = float(request.form['bid_amount'])
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(bid_amount) FROM bids")
        latest_bid_amount = cursor.fetchone()[0]
        if latest_bid_amount is None or bid_amount > latest_bid_amount:
            bidder_id = "User"  # You can replace this with actual user authentication
            current_time = datetime.datetime.now()
            cursor.execute("INSERT INTO bids (bidder_id, bid_amount, bid_time) VALUES (:1, :2, :3)", (bidder_id, bid_amount, current_time))
            connection.commit()
            cursor.close()
            return 'Bid placed successfully!'
        else:
            cursor.close()
            return 'Your bid must be higher than the current highest bid.'

if __name__ == '__main__':
    app.run(debug=True)
