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