"""
Go Where Ah? — Web Backend (Flask)
====================================
This is the backend API that powers the website.
It uses the Anthropic API with web search to find restaurant suggestions.

Requirements:
    pip install flask flask-cors anthropic

Run locally:
    python app.py

Then open index.html in your browser, or serve both with any static host.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import anthropic
import os

app = Flask(__name__)
CORS(app, origins=["https://clai-designs.github.io", "http://localhost:5000", "http://127.0.0.1:5500"])

# ── Config ──────────────────────────────────────────────
# Set this as an environment variable on your hosting platform
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY_HERE")
anthropic_client  = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ── Data ────────────────────────────────────────────────

MALLS = [
    ("ION Orchard", "Orchard MRT"),
    ("Ngee Ann City (Takashimaya)", "Orchard MRT"),
    ("313@Somerset", "Somerset MRT"),
    ("Orchard Gateway", "Somerset MRT"),
    ("Plaza Singapura", "Dhoby Ghaut MRT"),
    ("The Centrepoint", "Somerset MRT"),
    ("Wisma Atria", "Orchard MRT"),
    ("Mandarin Gallery", "Orchard MRT"),
    ("Paragon", "Orchard MRT"),
    ("Lucky Plaza", "Orchard MRT"),
    ("Far East Plaza", "Orchard MRT"),
    ("Tanglin Mall", "Orchard MRT"),
    ("Marina Bay Sands Shoppes", "Bayfront MRT"),
    ("Raffles City Shopping Centre", "City Hall MRT"),
    ("Suntec City Mall", "Esplanade MRT"),
    ("CityLink Mall", "City Hall MRT"),
    ("Bugis Junction", "Bugis MRT"),
    ("Bugis+", "Bugis MRT"),
    ("Funan", "City Hall MRT"),
    ("VivoCity", "HarbourFront MRT"),
    ("HarbourFront Centre", "HarbourFront MRT"),
    ("Parkway Parade", "Marine Parade"),
    ("i12 Katong", "Paya Lebar MRT"),
    ("Paya Lebar Quarter (PLQ)", "Paya Lebar MRT"),
    ("Tampines Mall", "Tampines MRT"),
    ("Century Square", "Tampines MRT"),
    ("Tampines 1", "Tampines MRT"),
    ("White Sands", "Pasir Ris MRT"),
    ("Bedok Mall", "Bedok MRT"),
    ("Downtown East", "Pasir Ris MRT"),
    ("Nex", "Serangoon MRT"),
    ("Compass One", "Sengkang MRT"),
    ("Hougang Mall", "Hougang MRT"),
    ("Northpoint City", "Yishun MRT"),
    ("Causeway Point", "Woodlands MRT"),
    ("Sun Plaza", "Sembawang MRT"),
    ("AMK Hub", "Ang Mo Kio MRT"),
    ("JEM", "Jurong East MRT"),
    ("Westgate", "Jurong East MRT"),
    ("IMM", "Jurong East MRT"),
    ("Jurong Point", "Boon Lay MRT"),
    ("West Mall", "Bukit Batok MRT"),
    ("Lot One", "Choa Chu Kang MRT"),
    ("Great World City", "Great World MRT"),
    ("Tiong Bahru Plaza", "Tiong Bahru MRT"),
    ("Clementi Mall", "Clementi MRT"),
    ("Holland Village Shopping Mall", "Holland Village MRT"),
    ("Novena Square / United Square", "Novena MRT"),
    ("Thomson Plaza", "Marymount MRT"),
    ("Bishan Junction 8", "Bishan MRT"),
    ("Toa Payoh HDB Hub", "Toa Payoh MRT"),
]

CUISINES = [
    ("Chinese", ["Dim Sum", "Roast Duck", "Char Kway Teow", "Hainanese Chicken Rice", "Wonton Noodles"]),
    ("Peranakan / Nyonya", ["Laksa", "Ayam Buah Keluak", "Kueh Pie Tee", "Babi Pongteh", "Chendol"]),
    ("Malay", ["Nasi Lemak", "Satay", "Rendang", "Mee Rebus", "Gado-Gado"]),
    ("Indian", ["Roti Prata", "Biryani", "Fish Head Curry", "Dosai", "Tandoori Chicken"]),
    ("Japanese", ["Sushi and Sashimi", "Ramen", "Tonkatsu", "Yakitori", "Udon"]),
    ("Korean", ["Korean BBQ", "Bibimbap", "Tteokbokki", "Kimchi Jjigae", "Japchae"]),
    ("Thai", ["Pad Thai", "Green Curry", "Tom Yum", "Mango Sticky Rice", "Som Tum"]),
    ("Vietnamese", ["Pho", "Banh Mi", "Bun Bo Hue", "Fresh Spring Rolls", "Bun Cha"]),
    ("Indonesian", ["Nasi Goreng", "Soto Ayam", "Gado-Gado", "Mie Goreng", "Martabak"]),
    ("Filipino", ["Adobo", "Sinigang", "Lechon", "Kare-Kare", "Halo-Halo"]),
    ("Italian", ["Pasta Carbonara", "Margherita Pizza", "Risotto", "Tiramisu", "Osso Buco"]),
    ("French", ["Steak Frites", "Coq au Vin", "Creme Brulee", "Croissant", "Bouillabaisse"]),
    ("Western", ["Fish and Chips", "Roast", "Shepherd's Pie", "Full English Breakfast", "Bangers and Mash"]),
    ("American", ["Burgers", "BBQ Ribs", "Mac and Cheese", "Clam Chowder", "Buffalo Wings"]),
    ("Mexican", ["Tacos", "Burritos", "Nachos with Guacamole", "Enchiladas", "Chiles Rellenos"]),
    ("Middle Eastern", ["Shawarma", "Falafel", "Hummus", "Kebab", "Lamb Biryani"]),
    ("Vegetarian / Vegan", ["Buddha Bowl", "Cauliflower Steak", "Jackfruit Curry", "Falafel Wrap", "Mushroom Wellington"]),
    ("Seafood", ["Chilli Crab", "Black Pepper Crab", "Lobster Thermidor", "Oysters", "Grilled Fish"]),
    ("Fusion / Modern Asian", ["Salted Egg Croissant", "Truffle Soba", "Laksa Pasta", "Miso Black Cod", "Matcha Tiramisu"]),
    ("Cafe / Brunch", ["Eggs Benedict", "Avocado Toast", "Pancakes", "Acai Bowl", "Shakshuka"]),
    ("Hotpot / Steamboat", ["Mala Hotpot", "Taiwanese Shabu-Shabu", "Yong Tau Foo", "Tom Yum Steamboat", "Japanese Shabu-Shabu"]),
]

RESTAURANT_PROMPT = """\
You are a Singapore food expert with access to the web.

Search and find 2-3 real restaurants serving {cuisine} food inside or directly
attached to {mall} in Singapore.

Rules:
- Only include restaurants that genuinely exist inside or right next to that mall.
- Prefer places with Google ratings between 3.5 and 5.0 stars.
- If fewer than 2 relevant restaurants exist, suggest nearby alternatives and note they are nearby.
- For each restaurant provide: Name, Google rating, number of reviews, one-sentence summary, must-try dish.

Respond in this EXACT pipe-delimited format, one restaurant per line, no extra text:

RESTAURANT_1|Name|4.2|320|Great family dim sum, can get crowded on weekends|Har Gow
RESTAURANT_2|Name|4.0|180|Cosy spot with generous portions|Tonkatsu Set
RESTAURANT_3|Name|4.5|95|Hidden gem with authentic flavours|Laksa

Output only the RESTAURANT_ lines. Nothing else.\
"""

# ── Routes ───────────────────────────────────────────────

@app.route("/api/spin", methods=["GET"])
def spin():
    """Return a random mall + cuisine pair."""
    mall_name, mrt = random.choice(MALLS)
    cuisine_name, dishes = random.choice(CUISINES)
    dish = random.choice(dishes)
    return jsonify({
        "mall": mall_name,
        "mrt": mrt,
        "cuisine": cuisine_name,
        "dish": dish,
    })

@app.route("/api/mall", methods=["GET"])
def spin_mall():
    """Return a random mall only."""
    mall_name, mrt = random.choice(MALLS)
    return jsonify({"mall": mall_name, "mrt": mrt})

@app.route("/api/cuisine", methods=["GET"])
def spin_cuisine():
    """Return a random cuisine only."""
    cuisine_name, dishes = random.choice(CUISINES)
    dish = random.choice(dishes)
    return jsonify({"cuisine": cuisine_name, "dish": dish})

@app.route("/api/restaurants", methods=["GET"])
def get_restaurants():
    """Fetch live restaurant suggestions using Anthropic + web search."""
    mall    = request.args.get("mall", "")
    cuisine = request.args.get("cuisine", "")
    if not mall or not cuisine:
        return jsonify({"error": "mall and cuisine are required"}), 400

    prompt = RESTAURANT_PROMPT.format(mall=mall, cuisine=cuisine)
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in response.content if hasattr(b, "text"))
        restaurants = []
        for line in text.strip().splitlines():
            line = line.strip()
            if not line.startswith("RESTAURANT_"):
                continue
            parts = line.split("|")
            if len(parts) < 6:
                continue
            _, name, rating_str, reviews_str, summary, dish = parts[:6]
            try:
                rating = float(rating_str.strip())
            except ValueError:
                rating = 4.0
            restaurants.append({
                "name":    name.strip(),
                "rating":  rating,
                "reviews": reviews_str.strip(),
                "summary": summary.strip(),
                "dish":    dish.strip(),
            })
        return jsonify({"restaurants": restaurants})
    except Exception as e:
        print(f"[Anthropic] Error: {e}")
        return jsonify({"restaurants": [], "error": str(e)}), 500

@app.route("/api/malls", methods=["GET"])
def list_malls():
    return jsonify([{"name": m[0], "mrt": m[1]} for m in MALLS])

@app.route("/api/cuisines", methods=["GET"])
def list_cuisines():
    return jsonify([c[0] for c in CUISINES])

@app.route("/", methods=["GET"])
def index():
    return "Go Where Ah? API is running! Visit your frontend to use the app."

if __name__ == "__main__":
    app.run(debug=True, port=5000)
