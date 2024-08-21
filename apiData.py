from flask import Flask,request,jsonify
import requests
from bs4 import BeautifulSoup as beauty



app = Flask(__name__)
def getData(results):
    data = []
    for row in results:
        data.extend([td.get_text(strip=True) for td in row.find_all('td')])
        break
    return data
  
def contains_no_numeric(s):
    return not any(char.isdigit() for char in s)
  
  
@app.route("/")
def home():
  



      URL = "https://vegetablemarketprice.com/market/puducherry/today"

      try:
          page = requests.get(URL)
          page.raise_for_status()  
      except requests.RequestException as e:
          print(f"Request failed: {e}")
          exit()

      soup = beauty(page.content, "html.parser")
      results = soup.find_all('tr', class_="todayVegetableTableRows")
      gotData = getData(results)

      # print(type(gotData))


      filtered_data = [item for index, item in enumerate(gotData) if (index % 6) != 0]
      # print(filtered_data)

      name_extracted_data = [item for item in filtered_data if contains_no_numeric(item)]
      # print(name_extracted_data)
      # print(len(name_extracted_data))

      fully_filtered_data = [item for index, item in enumerate(filtered_data) if (index % 5) != 0 ]
      # print(fully_filtered_data)

      grouped_data = [fully_filtered_data[i:i + 4] for i in range(0, len(fully_filtered_data), 4)]

      # print(len(fully_filtered_data))

      # print(grouped_data)
      # print(len(grouped_data))

      key_value_pairs = dict(zip(name_extracted_data, grouped_data))

      print(key_value_pairs)
      print(key_value_pairs['Onion Big'])


      for key, values in key_value_pairs.items():
          print(f"{key}:")
          for value in values:
              print(f" - {value}")


      return jsonify(key_value_pairs)


if __name__ == "__main__":
  app.run(debug=True)