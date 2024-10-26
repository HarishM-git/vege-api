from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def getData(results):
    data = []
    for row in results:
        data.extend([td.get_text(strip=True) for td in row.find_all('td')])
        break
    return data

def contains_no_numeric(s):
    return not any(char.isdigit() for char in s)

def fetch_image_url(query):
    search_url = f"https://www.google.com/search?hl=en&tbm=isch&q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(search_url, headers=headers)
    
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    images = soup.find_all("img")
    
    if images:
        return images[1]['src'] 
    
    return None

@app.route("/")
def home():
    URL = "https://vegetablemarketprice.com/market/puducherry/today"

    try:
        page = requests.get(URL)
        page.raise_for_status()  
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return jsonify({"error": "Failed to fetch data from the market price site"}), 500

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all('tr', class_="todayVegetableTableRows")
    gotData = getData(results)

    filtered_data = [item for index, item in enumerate(gotData) if (index % 6) != 0]
    name_extracted_data = [item for item in filtered_data if contains_no_numeric(item)]
    fully_filtered_data = [item for index, item in enumerate(filtered_data) if (index % 5) != 0]
    grouped_data = [fully_filtered_data[i:i + 4] for i in range(0, len(fully_filtered_data), 4)]

    key_value_pairs = dict(zip(name_extracted_data, grouped_data))

    for item in key_value_pairs.keys():
        image_url = fetch_image_url(item)
        key_value_pairs[item].append(image_url) 

    return jsonify(key_value_pairs)

if __name__ == "__main__":
    app.run(debug=True)
