from flask import Flask, request, jsonify
import logging

# === App Setup ===
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# === In-memory store for dropdown data ===
latest_dropdown_data = {}

# === POST /update-dropdowns → from FileMaker ===
@app.route("/update-dropdowns", methods=["POST"])
def update_dropdowns():
    global latest_dropdown_data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    latest_dropdown_data = data
    logging.info("✅ Dropdowns received and stored")
    return jsonify({"status": "stored", "keys": list(data.keys())}), 200

# === GET /dropdowns → Bubble fetches live data ===
@app.route("/dropdowns", methods=["GET"])
def serve_dropdowns():
    global latest_dropdown_data
    if not latest_dropdown_data:
        return jsonify({"error": "No dropdown data available"}), 404
    return jsonify(latest_dropdown_data)

# === GET / → Just for sanity check
@app.route("/", methods=["GET"])
def home():
    return "✅ Bubble Dropdown Service is Running", 200

# === Only used for local testing (Render uses gunicorn) ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)