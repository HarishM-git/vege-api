from flask import Flask, jsonify
import requests
import aiohttp
import asyncio

app = Flask(__name__)

def get_data(results):
    data = []
    for row in results:
        data.extend([td.get_text(strip=True) for td in row.find_all('td')])
        break
    return data

def contains_no_numeric(s):
    return not any(char.isdigit() for char in s)

# Fetch an image URL using Google Custom Search API
async def fetch_image_url(session, query, api_key, cse_id):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={cse_id}&searchType=image&key={api_key}&num=1"

    try:
        async with session.get(search_url) as response:
            if response.status != 200:
                print(f"Failed to fetch {query}: HTTP status {response.status}")
                return None

            data = await response.json()
            if "items" in data and len(data["items"]) > 0:
                return data["items"][0]["link"]
    except Exception as e:
        print(f"Error fetching image for {query}: {e}")
    return None

# Fetch multiple image URLs asynchronously
async def fetch_images(queries, api_key, cse_id):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_image_url(session, query, api_key, cse_id) for query in queries]
        return await asyncio.gather(*tasks)

@app.route("/")
def home():
    URL = "https://vegetablemarketprice.com/market/puducherry/today"

    try:
        page = requests.get(URL, timeout=10)
        page.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return jsonify({"error": "Failed to fetch data from the market price site"}), 500

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all('tr', class_="todayVegetableTableRows")
    got_data = get_data(results)

    filtered_data = [item for index, item in enumerate(got_data) if (index % 6) != 0]
    name_extracted_data = [item for item in filtered_data if contains_no_numeric(item)]
    fully_filtered_data = [item for index, item in enumerate(filtered_data) if (index % 5) != 0]
    grouped_data = [fully_filtered_data[i:i + 4] for i in range(0, len(fully_filtered_data), 4)]

    key_value_pairs = dict(zip(name_extracted_data, grouped_data))
    queries = list(key_value_pairs.keys())

    api_key = 'AIzaSyDxR63sLRIeOV4kICHxSZpF86unsa7RZt8'  
    cse_id = 'e30fe9773fa4641af' 
    
    # Fetch image URLs
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    image_urls = loop.run_until_complete(fetch_images(queries, api_key, cse_id))

    # Add image URLs to the data
    for i, item in enumerate(key_value_pairs.keys()):
        key_value_pairs[item].append(image_urls[i])

    return jsonify(key_value_pairs)

if __name__ == "__main__":
    app.run(debug=True)
