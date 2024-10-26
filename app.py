from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
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

async def fetch_image_url(session, query):
    search_url = f"https://www.google.com/search?hl=en&tbm=isch&q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    try:
        async with session.get(search_url, headers=headers) as response:
            if response.status != 200:
                return None
            
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            images = soup.find_all("img")
            
            if images:
                return images[1]['src']  # Return the second image (first one is usually a logo)
    except Exception as e:
        print(f"Error fetching image for {query}: {e}")
    return None

async def fetch_images(queries):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_image_url(session, query) for query in queries]
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

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all('tr', class_="todayVegetableTableRows")
    got_data = get_data(results)

    filtered_data = [item for index, item in enumerate(got_data) if (index % 6) != 0]
    name_extracted_data = [item for item in filtered_data if contains_no_numeric(item)]
    fully_filtered_data = [item for index, item in enumerate(filtered_data) if (index % 5) != 0]
    grouped_data = [fully_filtered_data[i:i + 4] for i in range(0, len(fully_filtered_data), 4)]

    key_value_pairs = dict(zip(name_extracted_data, grouped_data))
    queries = list(key_value_pairs.keys())
    
    # Fetch images asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    image_urls = loop.run_until_complete(fetch_images(queries))

    for i, item in enumerate(key_value_pairs.keys()):
        key_value_pairs[item].append(image_urls[i]) 

    return jsonify(key_value_pairs)

if __name__ == "__main__":
    app.run(debug=True)
