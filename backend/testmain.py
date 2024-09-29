from flask import Flask, request, jsonify, render_template, send_file
import cv2
import numpy as np
import os
from dotenv import load_dotenv
import base64
from io import BytesIO
import random

app = Flask(__name__)
load_dotenv()

def analyze_distance(image):
    myopia_levels = [
        {"distance": 5, "diopters": -3.00, "description": "Mild myopia"},
        {"distance": 3, "diopters": -4.50, "description": "Moderate myopia"},
        {"distance": 1, "diopters": -7.00, "description": "High myopia"}
    ]
    chosen_level = random.choice(myopia_levels)
    return chosen_level["distance"]

def blur_image(image, distance):
    max_kernel_size = 5000  # Increased maximum blur kernel size
    kernel_size = int(distance * 10) + 1  # Increase the multiplying factor to make it blurrier
    kernel_size = min(max_kernel_size, max(1, kernel_size if kernel_size % 2 else kernel_size + 1))
    blurred_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    return blurred_image

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify(error="No image file"), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify(error="No selected file"), 400

        try:
            # Read the image file from the request
            file_bytes = np.frombuffer(file.read(), np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            # Check if the image was successfully loaded
            if image is None:
                return jsonify(error="Failed to decode image file"), 400

            distance = analyze_distance(image)
            blurred_image = blur_image(image, distance)
            
            # Convert images to base64 for display
            _, original_buffer = cv2.imencode('.png', image)
            _, blurred_buffer = cv2.imencode('.png', blurred_image)
            original_base64 = base64.b64encode(original_buffer).decode('utf-8')
            blurred_base64 = base64.b64encode(blurred_buffer).decode('utf-8')
            
            return render_template('result.html', 
                                   original_image=original_base64, 
                                   blurred_image=blurred_base64, 
                                   distance=distance)
        except Exception as e:
            return jsonify(error=str(e)), 500
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)