from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import schedule
import time
import os
from threading import Thread

app = Flask(__name__)

# MongoDB connection URI (use environment variable or hardcoded URI for testing)
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://harishdeepakh:v4m42ggQy9POGNHo@cluster1.n89f6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")
client = MongoClient(MONGODB_URI)

# Database and collection
db = client["store_data_db"]
collection = db["product_prices"]

# Endpoint for store owners to submit prices
@app.route('/api/submitPrice', methods=['POST'])
def submit_price():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Process each store type in the submitted data
    for store_name, products in data.items():
        # Each store's product list
        for product in products:
            # Insert each product with store name into the database
            new_price = {
                "store_name": store_name,
                "product_name": product.get("name"),
                "price": product.get("price"),
                "image_url": product.get("imageUrl"),
                "date_added": datetime.utcnow()
            }
            collection.insert_one(new_price)
    
    return jsonify({"message": "Data submitted successfully"}), 201

# Endpoint to fetch product prices
@app.route('/api/getItemPrices', methods=['GET'])
def get_item_prices():
    item_name = request.args.get("item")
    if not item_name:
        return jsonify({"error": "Please provide an item name"}), 400
    try:
        # Query MongoDB for prices
        prices = list(collection.find({"product_name": item_name}))
        if not prices:
            return jsonify({"message": f"No prices found for {item_name}"}), 404
        result = [
            {
                "store": price["store_name"],
                "name": price["product_name"],
                "price": price["price"],
                "imageUrl": price["image_url"],
                "date_added": price["date_added"]
            }
            for price in prices
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Scheduled task to process submissions at 12:00 PM
def process_submissions():
    print("Processing and updating database with new submissions")
    # Placeholder for processing logic

# Set up scheduling
schedule.every().day.at("12:00").do(process_submissions)

# Scheduler thread function
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Run app
if __name__ == '__main__':
    # Start the scheduler in a separate thread
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.start()
    app.run(debug=True)
