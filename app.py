from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Static image URLs mapped to vegetable names
static_images = {
    "Amaranth Leaves": "https://www.adaptiveseeds.com/wp-content/uploads/2014/12/amaranth-miriah-leaf-3-7.jpg",
    "Amla": "https://lukecoutinho.com/blog/wp-content/uploads/2021/12/The-Health-Benefits-of-Amla.jpg",
    "Ash gourd": "https://i0.wp.com/post.healthline.com/wp-content/uploads/2020/04/ash-gourd-1296x728-header.jpg?w=1155&h=1528",
    "Baby Corn": "https://thesimplesprinkle.com/wp-content/uploads/2022/09/roasted-baby-corn-3.jpg",
    "Banana Flower": "https://www.thespruceeats.com/thmb/P9NIPKyl8reVr4xvUSXJ96K6UYg=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Banana-Flower-5794d0285f9b58173b9cf879.jpg",
    "Beetroot": "https://media.post.rvohealth.io/wp-content/uploads/sites/3/2020/02/277432_2200-800x1200.jpg",
    "Bitter Gourd": "https://cdn.britannica.com/91/170791-050-13189FE2/bitter-melon.jpg",
    "Bottle Gourd": "https://m.media-amazon.com/images/I/61h4CqBu7EL.jpg",
    "Brinjal": "https://upload.wikimedia.org/wikipedia/commons/7/76/Solanum_melongena_24_08_2012_%281%29.JPG",
    "Brinjal (Big)": "https://smartyield.in/wp-content/uploads/2021/06/Big-brinjal-eggplant.png",
    "Broad Beans": "https://images.squarespace-cdn.com/content/v1/605d2d8f3dd39e6a5b1eae5f/1716656661197-DV9L056DGGW5UNW67UY5/favabeans.jpg",
    "Butter Beans": "https://southernbite.com/wp-content/uploads/2020/10/Southern-Lima-Beans.jpg",
    "Cabbage": "https://www.themediterraneandish.com/wp-content/uploads/2021/10/roasted-cabbage-recipe-3.jpg",
    "Capsicum": "https://upload.wikimedia.org/wikipedia/commons/d/da/Red_capsicum_and_cross_section.jpg",
    "Carrot": "https://ucarecdn.com/459eb7be-115a-4d85-b1d8-deaabc94c643/-/format/auto/-/preview/3000x3000/-/quality/lighter/",
    "Cauliflower": "https://dishingouthealth.com/wp-content/uploads/2022/12/GarlicParmesanCauliflower_Styled1.jpg",
    "Cluster beans": "https://urbanthottam.com/wp-content/uploads/2020/11/Cluster-Beans_Ravichandra.jpg",
    "Coconut": "https://domf5oio6qrcr.cloudfront.net/medialibrary/13842/3f39961d-d850-4885-8ddc-d85186d1113a.jpg",
    "Colocasia": "https://www.gardenia.net/wp-content/uploads/2023/05/Colocasia-esculenta-Taro-796x533.webp",
    "Colocasia Leaves": "https://cookilicious.com/wp-content/uploads/2021/08/pathrode-patra-colocasia-pinwheels-4.jpg",
    "Coriander Leaves": "https://cookbook.pfeiffer.net.au/files/corianderPlant.jpg",
    "Corn": "https://cdn.britannica.com/36/167236-050-BF90337E/Ears-corn.jpg",
    "Cucumber": "https://wh.farm/wp-content/uploads/2022/09/SlicerCucumber-Featured.jpg",
    "Curry Leaves": "https://assets.bonappetit.com/photos/612fdd52349942e3b2e2863c/4:3/w_1417,h_1063,c_limit/Curry%20Leaves.jpg",
    "Dill Leaves": "https://static.toiimg.com/photo/84488358.cms",
    "Drumsticks": "https://vicfirth.com/cdn/shop/files/2000-X-2000-JPG-AH5A_Vic_Firth_American_Heritage_5A-1.jpg?v=1701882067&width=768",
    "Elephant Yam": "https://i.ytimg.com/vi/8snZfekKvig/maxresdefault.jpg",
    "Fenugreek Leaves": "https://images.squarespace-cdn.com/content/v1/5cef7b136434550001a53d10/98da7dcd-df30-448b-aa23-9d656700321e/Methi+Salad-6.jpg",
    "French Beans": "https://www.allrecipes.com/thmb/QnE2pw82Rr8B4xNIIodxOB7VzWA=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/238665-grilled-green-beans-mfs-4-f5ab1488b73d4798a7543d5353d3bf84.jpg",
    "Garlic": "https://i5.walmartimages.com/seo/Garlic-Bulb-Fresh-Whole-Each_a4f114d9-93ab-4d39-a8d6-9170536f57a9.f9f8e58c8e3e74894050c7c2267437e3.jpeg",
    "Ginger": "https://files.nccih.nih.gov/ginger-thinkstockphotos-531052216-square.jpg",
    "Green Chilli": "https://fruitboxco.com/cdn/shop/products/VG-CL-20_800x.jpg?v=1588920882",
    "Green Peas": "https://media.post.rvohealth.io/wp-content/uploads/2020/09/green-peas-thumb-1-732x549.jpg",
    "Ivy Gourd": "http://www.podilife.com/cdn/shop/articles/tindora.png?v=1636493948",
    "Ladies Finger": "https://onebay.in/cdn/shop/files/ladies-finger-green-short.jpg?v=1716800460&width=1946",
    "Lemon (Lime)": "https://i0.wp.com/images-prod.healthline.com/hlcmsresource/images/AN_images/lime-vs-lemon-1296x728-feature.jpg?w=1155&h=1528",
    "Mango Raw": "https://www.hindustantimes.com/ht-img/img/2024/05/14/1600x900/ripe_vs_raw_mangoes_1715684547387_1715684558894.jpg",
    "Mint Leaves": "https://m.media-amazon.com/images/I/815lDfelezL.jpg",
    "Mushroom": "https://cdn.britannica.com/90/236590-050-27422B8D/Close-up-of-mushroom-growing-on-field.jpg",
    "Mustard Leaves": "https://www.highmowingseeds.com/media/catalog/product/cache/95cbc1bb565f689da055dd93b41e1c28/2/4/2486-5.jpg",
    "Onion Big": "https://i.redd.it/c347ieo0hqr91.jpg",
    "Onion Green": "https://www.simplyrecipes.com/thmb/Bhac01hThuBbQJ27vmRwHPloD2k=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Simply-Recipes-The-Best-Way-To-Store-Green-Onions-METHOD-1A-e625d1c233384353b53e49615f93c485.jpg",
    "Onion Small": "http://onebay.in/cdn/shop/files/Small-onion-seed.jpg?v=1716807556",
    "Potato": "https://cdn.apartmenttherapy.info/image/upload/f_auto,q_auto:eco,c_fill,g_auto,w_1500,ar_3:2/k%2FDesign%2F2024%2F08-2024%2Ftypes-of-potatoes-update%2Fk-types-of-potatoes_lead",
    "Pumpkin": "https://s7d6.scene7.com/is/image/bjs/309029",
    "Radish": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Radish_3371103037_4ab07db0bf_o.jpg",
    "Raw Banana (Plantain)": "https://i0.wp.com/images-prod.healthline.com/hlcmsresource/images/topic_centers/Food-Nutrition/1296x728_Plantains-Nutrition_Facts_and_Health_Benefits.jpg?w=1155&h=1528",
    "Ridge Gourd": "https://static.toiimg.com/photo/79265520.cms",
    "Shallot (Pearl Onion)": "https://www.innit.com/public/recipes/images/1002581--146856609-en-US-0_s500.jpg",
    "Snake Gourd": "https://cdn.britannica.com/45/190845-050-1EAF48FA/snake-gourds.jpg",
    "Sorrel": "https://exat8rt6fi5.exactdn.com/wp-content/uploads/2022/05/red-sorrel-01-600x600.jpg?strip=all&lossy=1&ssl=1",
    "Spinach": "https://i0.wp.com/post.healthline.com/wp-content/uploads/2019/05/spinach-1296x728-header.jpg?w=1155&h=1528",
    "Sweet Potato": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Ipomoea_batatas_006.JPG/800px-Ipomoea_batatas_006.JPG",
    "Tomato": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Tomato_je.jpg/1200px-Tomato_je.jpg"
}


def get_data(results):
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
        page = requests.get(URL, timeout=10)
        page.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return jsonify({"error": "Failed to fetch data from the market price site"}), 500

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all('tr', class_="todayVegetableTableRows")
    got_data = get_data(results)

    # Filter and organize the data
    filtered_data = [item for index, item in enumerate(got_data) if (index % 6) != 0]
    name_extracted_data = [item for item in filtered_data if contains_no_numeric(item)]
    fully_filtered_data = [item for index, item in enumerate(filtered_data) if (index % 5) != 0]
    grouped_data = [fully_filtered_data[i:i + 4] for i in range(0, len(fully_filtered_data), 4)]

    # Create key-value pairs and append static image URLs
    key_value_pairs = {}
    for name in name_extracted_data:
        prices = grouped_data[name_extracted_data.index(name)]
        image_url = static_images.get(name, None)  # Get the image URL or None if not found
        key_value_pairs[name] = prices + [image_url]

    return jsonify(key_value_pairs)

if __name__ == "__main__":
    app.run(debug=True)
