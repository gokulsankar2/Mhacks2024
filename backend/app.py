from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from your React frontend

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        app.logger.error("No video part")
        return jsonify({"error": "No video part"}), 400

    file = request.files['video']
    if file.filename == '':
        app.logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400

    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(filename)
        app.logger.info(f"File saved to {filename}")
        return jsonify({"message": "File uploaded successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error saving file: {e}")
        return jsonify({"error": "Failed to save file"}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)