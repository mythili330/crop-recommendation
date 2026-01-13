from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging
import traceback
import openai

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = "raitusaarathi_secret_key"
CORS(app)

logging.basicConfig(level=logging.INFO)

# ---------------- OPENAI CONFIG ----------------
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    logging.warning("OpenAI API key not found. GPT responses will fallback to demo.")

# ---------------- CROP RECOMMENDATION ----------------
def recommend_crops(soil_type, location, season, rainfall_type):
    crops_data = {
        "Rice": {"soil": "clay", "rainfall": "high", "season": "rainy", "locations": ["andhra", "telangana", "bihar", "wb"]},
        "Wheat": {"soil": "clay", "rainfall": "medium", "season": "winter", "locations": ["punjab", "up", "haryana", "mp"]},
        "Maize": {"soil": "loamy", "rainfall": "medium", "season": "rainy", "locations": ["karnataka", "telangana", "ap"]},
        "Potatoes": {"soil": "sandy", "rainfall": "medium", "season": "winter", "locations": ["up", "bihar", "west bengal"]},
        "Carrots": {"soil": "sandy", "rainfall": "medium", "season": "winter", "locations": ["karnataka", "tn", "up"]},
        "Cotton": {"soil": "clay", "rainfall": "high", "season": "summer", "locations": ["maharashtra", "telangana", "gujarat"]},
        "Peanuts": {"soil": "sandy", "rainfall": "low", "season": "summer", "locations": ["gujarat", "ap", "karnataka"]},
        "Tomatoes": {"soil": "loamy", "rainfall": "medium", "season": "summer", "locations": ["karnataka", "ap", "telangana"]},
        "Cabbage": {"soil": "loamy", "rainfall": "medium", "season": "winter", "locations": ["up", "bihar", "punjab"]},
        "Watermelons": {"soil": "sandy", "rainfall": "high", "season": "summer", "locations": ["karnataka", "telangana", "ap"]},
        "Millets": {"soil": "sandy", "rainfall": "low", "season": "summer", "locations": ["rajasthan", "karnataka", "ap"]},
        "Sorghums": {"soil": "sandy", "rainfall": "low", "season": "summer", "locations": ["maharashtra", "karnataka", "ap"]}
    }

    market_prices = {
        "Rice": "₹25/kg", "Wheat": "₹22/kg", "Maize": "₹20/kg", "Carrots": "₹30/kg",
        "Potatoes": "₹15/kg", "Cabbage": "₹18/kg", "Cotton": "₹120/kg",
        "Sorghums": "₹28/kg", "Watermelons": "₹12/kg", "Tomatoes": "₹20/kg",
        "Millets": "₹35/kg", "Peanuts": "₹40/kg"
    }

    fertilizer_advice = {
        "Rice": "Urea, DAP, Potash", "Wheat": "Urea, Zinc Sulphate, Potash",
        "Maize": "Urea, DAP, Potash, Boron", "Potatoes": "NPK 10:26:26, Urea, MOP",
        "Carrots": "Farmyard Manure, Superphosphate", "Cotton": "Urea, Potash, DAP",
        "Peanuts": "Gypsum, Potash, SSP", "Tomatoes": "Compost, NPK 19:19:19",
        "Cabbage": "NPK 15:15:15, Urea", "Watermelons": "Superphosphate, Potash",
        "Millets": "DAP, Urea", "Sorghums": "SSP, Potash, Urea"
    }

    # Normalize inputs (case-insensitive)
    soil_type = soil_type.lower()
    season = season.lower()
    location = location.lower()
    rainfall_type = rainfall_type.lower()

    scores = {}
    for crop, data in crops_data.items():
        score = 0
        if soil_type == data["soil"]:
            score += 2
        if rainfall_type == data["rainfall"]:
            score += 2
        if season == data["season"]:
            score += 2
        if location in data["locations"]:
            score += 2
        scores[crop] = score

    recommended_crops = [crop for crop, sc in scores.items() if sc >= 4]

    # Advice
    if rainfall_type == "low":
        irrigation_advice = "Use drip irrigation and drought-resistant crops."
    elif rainfall_type == "high":
        irrigation_advice = "Ensure proper drainage and raised beds."
    else:
        irrigation_advice = "Normal irrigation is sufficient."

    if season == "summer":
        season_advice = "Hot season crops are best suited."
    elif season == "winter":
        season_advice = "Cool season crops are recommended."
    elif season == "rainy":
        season_advice = "Rain-fed crops will thrive."
    else:
        season_advice = "General crops suitable for all seasons."

    return {
        "Recommended Crops": recommended_crops,
        "Irrigation Advice": irrigation_advice,
        "Season Advice": season_advice,
        "Market Prices": {crop: market_prices.get(crop, "N/A") for crop in recommended_crops},
        "Fertilizers_advice": {crop: fertilizers.get(crop, "N/A") for crop in recommended_crops}
    }

# ---------------- ROUTES ----------------
@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/assistant")
def assistant():
    return render_template("assistant.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    recommendations = recommend_crops(
        data["soil_type"], data["location"], data["season"], data["rainfall"]
    )
    return jsonify({"success": True, **recommendations})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    language = data.get("language", "English")

    if not message:
        return jsonify({"reply": "⚠️ Please type a message."})

    if openai.api_key:
        try:
            prompt = f"""
            You are RaituSaarthi, a friendly AI farming assistant.
            Answer this farmer's question in {language}:
            "{message}"
            Give useful advice about crops, soil, weather, or farming techniques.
            """
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250
            )
            reply = response.choices[0].message.content.strip()
            return jsonify({"reply": reply})
        except Exception as e:
            logging.error("OpenAI API call failed:\n%s", traceback.format_exc())

    # Fallback if API fails or key missing
    return jsonify({"reply": f"You said: '{message}'. This is a demo reply!"})

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
