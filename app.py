from flask import Flask, request, jsonify
import requests
import logging
import json
import re

# === Config ===
WIX_URL = "https://aivs.uk/_functions/post_received"
WIX_TIMEOUT = 10  # seconds
WIX_SHARED_SECRET = "michael-2025-secret-key"  # 🔐 must match what Wix expects

# === App Setup ===
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# === POST / → forwards JSON to Wix ===
@app.route("/", methods=["POST"])
def forward_json():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "No JSON received"}), 400

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": WIX_SHARED_SECRET
    }

    try:
        logging.info(f"Forwarding to Wix: {data}")
        response = requests.post(WIX_URL, json=data, headers=headers, timeout=WIX_TIMEOUT)
        return jsonify({
            "status": "forwarded",
            "wix_status": response.status_code,
            "wix_response": response.text
        }), 200

    except requests.exceptions.Timeout:
        logging.error("Timeout occurred when forwarding to Wix")
        return jsonify({"error": "Timeout forwarding to Wix"}), 504

    except requests.exceptions.RequestException as e:
        logging.error(f"Error forwarding to Wix: {str(e)}")
        return jsonify({"error": str(e)}), 502

# === GET / → Health Check ===
@app.route("/", methods=["GET"])
def ping():
    return "FileMaker → Render → Wix API ready.", 200

# === POST /update-dropdowns → Saves dropdown JSON from FileMaker ===
@app.route("/update-dropdowns", methods=["POST"])
def update_dropdowns():
    try:
        # Step 1: Read raw bytes and decode like iconv -c (strip invalid UTF-8)
        raw_bytes = request.data
        cleaned_str = raw_bytes.decode("utf-8", errors="ignore")  # ⬅️ mimics iconv -c

        print("🔍 RAW BODY RECEIVED (first 300 chars):", cleaned_str[:300])

        # Step 2: Strip smart quotes, BOM, zero-width/invisible characters
        cleaned_str = (
            cleaned_str.replace("“", '"')
                       .replace("”", '"')
                       .replace("‘", "'")
                       .replace("’", "'")
                       .replace("\ufeff", "")  # BOM
        )
        cleaned_str = re.sub(r"[\u200b-\u200f]", "", cleaned_str)

        # Step 3: Parse cleaned JSON
        data = json.loads(cleaned_str)

        # Step 4: Save it to a file
        with open("dropdowns.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print("✅ dropdowns.json saved successfully.")
        return jsonify({"status": "saved"}), 200

    except Exception as e:
        print("❌ ERROR saving dropdowns:", str(e))
        return jsonify({"error": str(e)}), 400

# === GET /dropdowns.json → Wix frontend fetches dropdowns ===
@app.route("/dropdowns.json", methods=["GET"])
def serve_dropdowns():
    try:
        with open("dropdowns.json", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 404