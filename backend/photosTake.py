from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests  # For making requests to the Gemini API

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from your React frontend

UPLOAD_FOLDER = 'uploads/'
PROCESSED_FOLDER = 'processed/' # To save processed images if needed
GEMINI_API_URL = 'https://api.gemini.com/process_image'  # Replace with actual Gemini API URL
GEMINI_API_KEY = 'your_gemini_api_key'  # Replace with your Gemini API key
PROMPT = 'your_specific_prompt'  # The specific prompt for the Gemini API

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    upload_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(upload_path)

        # Process the file with Gemini API
        processed_data = process_with_gemini(upload_path)

        # Save processed image if needed
        processed_filename = os.path.join(PROCESSED_FOLDER, file.filename)
        with open(processed_filename, 'wb') as processed_file:
            processed_file.write(processed_data)

        return jsonify({"message": "File uploaded and processed successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save and process file: {e}"}), 500

def process_with_gemini(image_path):
    """
    Process the image with the Gemini API.

    :param image_path: Path to the image to be processed.
    :return: Processed image data.
    """
    with open(image_path, 'rb') as image_file:
        files = {'image': image_file}
        data = {'prompt': PROMPT}
        headers = {'Authorization': f'Bearer {GEMINI_API_KEY}'}  # Add your authorization method if needed

        response = requests.post(GEMINI_API_URL, files=files, data=data, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to process image with Gemini API: {response.text}")

        # Assuming the response contains the processed image data directly
        return response.content

if __name__ == '__main__':
    app.run(port=5000, debug=True)