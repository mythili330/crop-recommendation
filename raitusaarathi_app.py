from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import torch
from transformers import pipeline
from PIL import Image
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image

# Import your recommendation logic from app.py
from app import recommend_crops, market_prices,fertilizer_advice

app = Flask(__name__)
CORS(app)

# ---------------- AI MODELS ----------------

# 1️⃣ Text-generation model (HuggingFace)
model_name = "google/flan-t5-small"
text_generator = pipeline(
    "text2text-generation",
    model=model_name,
    device=0 if torch.cuda.is_available() else -1
)

# 2️⃣ Soil image classification model
SOIL_MODEL_PATH = "models/soil_model/final_soil_model.h5"
soil_model = load_model(SOIL_MODEL_PATH)
SOIL_CLASSES = sorted(os.listdir("dataset/train"))  # Example: ['black', 'clay', 'red', 'sandy']

def predict_soil(image_path):
    """Predict soil type from an uploaded image"""
    img = keras_image.load_img(image_path, target_size=(128, 128))
    x = keras_image.img_to_array(img) / 255.0
    x = np.expand_dims(x, axis=0)

    preds = soil_model.predict(x)
    idx = int(np.argmax(preds))
    label = SOIL_CLASSES[idx]
    confidence = float(np.max(preds))
    return f"Soil Type: {label} (Confidence: {confidence:.2f})"

# ---------------- Fertilizer Advice ----------------

fertilizer_advice = {
    "Rice": "Use Urea, DAP, and Potash in 3:2:1 ratio during transplanting.",
    "Wheat": "Apply NPK 120:60:40 kg/ha; prefer urea and DAP.",
    "Maize": "Use NPK 100:75:50 with micronutrients like zinc.",
    "Cotton": "Provide nitrogen and potassium-rich fertilizer every 3 weeks.",
    "Groundnut": "Add gypsum at flowering and maintain phosphorus levels.",
    "Sugarcane": "Apply NPK 275:62:112 kg/ha and regular organic compost.",
    "Soybean": "Use Rhizobium inoculant and phosphorus-rich fertilizers."
}

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").lower()
    language = data.get("language", "English")

    if not user_message:
        return jsonify({"success": False, "reply": "Message cannot be empty."})

    # Check if user asks for crop or fertilizer recommendations
    if "recommend" in user_message or "crop" in user_message:
        # You can modify these defaults to come from frontend
        soil_type = "clay"
        season = "summer"
        rainfall = "low"

        recommended_crops, irrigation, season_advice = recommend_crops(soil_type, season, rainfall)

        market_data = {crop: market_prices.get(crop, "N/A") for crop in recommended_crops}
        fert_data = {crop: fertilizer_advice.get(crop, "General NPK recommended.") for crop in recommended_crops}

        reply = (
            f"✅ Recommended crops: {', '.join(recommended_crops)}.\n"
            f"💧 Irrigation advice: {irrigation}.\n"
            f"🌦️ Seasonal advice: {season_advice}.\n"
            f"📈 Market prices: {market_data}.\n"
            f"🌿 Fertilizer advice: {fert_data}."
        )

    elif "fertilizer advice" in user_message:
        reply = "Here’s some general fertilizer advice:\n" + "\n".join(
            [f"{crop}: {advice}" for crop, advice in fertilizer_advice.items()]
        )

    else:
        # Fallback to AI text generation (general chatbot)
        try:
            response = text_generator(user_message, max_length=200)
            reply = response[0]["generated_text"]
        except Exception as e:
            print("Model error:", e)
            reply = "Sorry, I’m unable to answer right now."

    return jsonify({
        "success": True,
        "reply": reply,
        "language": language,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/analyze-image", methods=["POST"])
def analyze_uploaded_image():
    if "image" not in request.files:
        return jsonify({"success": False, "result": "No image uploaded."})

    image_file = request.files["image"]
    os.makedirs("uploads", exist_ok=True)
    image_path = os.path.join("uploads", image_file.filename)
    image_file.save(image_path)

    result = predict_soil(image_path)
    return jsonify({"success": True, "result": result})

# ---------------- RUN APP ----------------

if __name__ == "__main__":
    print("🚀 Starting RaituSaarthi AI Backend (Soil + Crop + Chat + Fertilizer)...")
    app.run(debug=True, host="0.0.0.0", port=5000)
