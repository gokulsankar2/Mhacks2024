from flask import Flask, request, jsonify
import cv2
import numpy as np
from groq import Groq
import requests

app = Flask(__name__)


class Client:
    def __init__(self, API_KEY):
        self.api_key = API_KEY

    def analyze_image(self, image):
        # Convert image to JPEG bytes
        _, img_encoded = cv2.imencode('.jpg', image)
        img_bytes = img_encoded.tobytes()

        # API request to Groq LLM
        url = 'https://api.groq.ai/analyze'  # Example endpoint, adjust as needed
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/octet-stream'
        }

        response = requests.post(url, headers=headers, data=img_bytes)

        if response.status_code == 200:
            response_json = response.json()
            distance = response_json.get('distance', None)
            return {'distance': distance}
        else:
            return {'error': 'Failed to analyze image'}

@app.route('/calibrate', methods=['POST'])
def calibrate_distance():
    file = request.files['image']
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    distance = analyze_distance(image)
    return jsonify(distance=distance)

def analyze_distance(image):
    # Convert the image to an appropriate format if needed
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # API call to Groq LLM to analyze the image
    response = Client.analyze_image(image_rgb)
    
    # Extract distance information from the response
    distance = response.get('distance')  # Assumes 'distance' is in the response
    return distance

def blur_image(image):
    kernel_size = 0
    # Use replicated border method
    blurred = np.zeros_like[image]
    mask = True
    blurred_region = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0, borderType=cv2.BORDER_REPLICATE)
    blurred[mask] = blurred_region[mask]
    return blurred

if __name__ == '__main__':
    app.run(debug=True)