import requests

data = {
  "superMarket": [
    {
      "name": "Amaranth Leaves",
      "price": "₹16 - 18",
      "imageUrl": "https://www.adaptiveseeds.com/wp-content/uploads/2014/12/amaranth-miriah-leaf-3-7.jpg"
    },
    {
      "name": "Amla",
      "price": "₹69 - 76",
      "imageUrl": "https://lukecoutinho.com/blog/wp-content/uploads/2021/12/The-Health-Benefits-of-Amla.jpg"
    },
    {
      "name": "Ash Gourd",
      "price": "₹18 - 20",
      "imageUrl": "https://i0.wp.com/post.healthline.com/wp-content/uploads/2020/04/ash-gourd-1296x728-header.jpg?w=1155&h=1528"
    }
  ]
  
}

response = requests.post("http://127.0.0.1:5000/api/submitPrice", json=data)
print(response.json())
