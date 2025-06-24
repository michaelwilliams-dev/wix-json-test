from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/", methods=["POST"])
def forward_json():
    data = request.get_json()

    wix_url = "https://aivs.uk/_functions/receive"  # 🔁 Replace with your Wix backend URL
    try:
        response = requests.post(wix_url, json=data, headers={"Content-Type": "application/json"})
        return jsonify({
            "status": "forwarded",
            "wix_status": response.status_code,
            "wix_response": response.text
        }), 200
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

@app.route("/", methods=["GET"])
def ping():
    return "FileMaker → Render → Wix API ready."