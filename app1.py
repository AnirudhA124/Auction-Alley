from flask import Flask, render_template

app = Flask(__name__)

# Sample data for demonstration
products = [
    {"name": "Product 1", "description": "Description of product 1", "starting_bid": 50, "scheduled_time": "2024-03-05T22:00:00"},
    {"name": "Product 2", "description": "Description of product 2", "starting_bid": 100, "scheduled_time": "2024-03-05T22:30:00"},
    {"name": "Product 3", "description": "Description of product 3", "starting_bid": 75, "scheduled_time": "2024-03-05T22:00:00"}
]

@app.route('/')
def index():
    return render_template('main.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
