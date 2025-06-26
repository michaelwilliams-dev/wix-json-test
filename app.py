from flask import Flask, request, jsonify
import requests
import logging
import json

# === Config ===
WIX_URL = "https://aivs.uk/_functions/post_received"
WIX_TIMEOUT = 10  # seconds
WIX_SHARED_SECRET = "michael-2025-secret-key"  # 🔐 must match what Wix expects

# === App Setup ===
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# === Root POST Endpoint — forwards to Wix ===
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

# === Health Check Endpoint ===
@app.route("/", methods=["GET"])
def ping():
    return "FileMaker → Render → Wix API ready.", 200

# === NEW: POST /update-dropdowns (from FileMaker) ===
@app.route("/update-dropdowns", methods=["POST"])
def update_dropdowns():
    try:
        # STEP 1: Raw body debug
        raw_body = request.data.decode("utf-8", errors="replace")
        print("🔍 RAW BODY RECEIVED:", raw_body)

        # STEP 2: Attempt to parse JSON
        data = json.loads(raw_body)

        # STEP 3: Save to file
        with open("dropdowns.json", "w") as f:
            json.dump(data, f, indent=2)

        return jsonify({"status": "saved"}), 200

    except Exception as e:
        print("❌ ERROR saving dropdowns:", str(e))
        return jsonify({"error": str(e)}), 400

# === GET /dropdowns.json (for Wix frontend) ===
@app.route("/dropdowns.json", methods=["GET"])
def serve_dropdowns():
    try:
        with open("dropdowns.json") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 404