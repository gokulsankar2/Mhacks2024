from flask import Flask, request, jsonify
import cv2
import numpy as np
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()  # Load environment variables

API_KEY = os.getenv('GROQ_API_KEY')

@app.route('/')
def home():
    return "Welcome to the Myopia Simulator!"

@app.route('/calibrate', methods=['POST'])
def calibrate_distance():
    if 'image' not in request.files:
        return jsonify(error="No image file"), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify(error="No selected file"), 400

    try:
        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        distance = analyze_distance(image)
        blurred_image = blur_image(image, distance)
        
        # Here you would typically save or process the blurred image
        # For now, we'll just return a success message
        return jsonify(distance=distance, message="Image processed successfully")
    except Exception as e:
        return jsonify(error=str(e)), 500

def analyze_distance(image):
    # This is a placeholder. You need to implement actual distance analysis
    # This might involve using a pre-trained model or another API
    return 5  # Placeholder distance value

def blur_image(image, distance):
    max_kernel_size = 31  # Maximum blur kernel size
    kernel_size = int(distance * 2) + 1  # Example of how to use distance
    kernel_size = min(max_kernel_size, max(1, kernel_size if kernel_size % 2 else kernel_size + 1))
    
    blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0, borderType=cv2.BORDER_REPLICATE)
    return blurred

if __name__ == '__main__':
    app.run(debug=True)