from flask import Flask, request, jsonify, render_template, send_file
import cv2
import numpy as np
import os
from dotenv import load_dotenv
import google.generativeai as genai
import shutil
import asyncio
import base64
from io import BytesIO
import random

app = Flask(__name__)
load_dotenv()

class File:
    def __init__(self, file_path: str, timestamp: str, display_name: str = None):
        self.file_path = file_path
        if display_name:
            self.display_name = display_name
        self.timestamp = timestamp
    def set_response(self, response):
       self.response = response
from datetime import datetime
class VideoGemini():
    def __init__(self, verbose: bool = False, delete: bool = True):
        #api key switching logic
        

        genai.configure(api_key=os.environ["API_KEY"])

        self.model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

        self.frames = []

        self.verbose = verbose

        self.delete = delete

        self.chat = self.model.start_chat(history=[])

        
        

    def upload_frame(self, file: File):
        if (self.verbose):
            print(file.file_path)
            print(f'Uploading: {file.file_path}...')
        response = genai.upload_file(path=file.file_path)
        file.set_response(response)
        if (self.verbose):
            print(f"Completed file upload")
            if (self.delete):
                print(f"Deleting local file at {file.file_path}")
        if (self.delete):
            os.remove(file.file_path)
            file.file_path = ""
        self.frames.append(file)

    def _build_request(self, query:str = None):
        request = []
        if (query):
            request.append(query)
        for frame in self.frames:
            request.append(frame.timestamp)
            request.append(frame.response)
        return request
    
    async def get_response_async(self):
        request = self._build_request()
        resp = self.chat.send_message(request)
        print(resp.text)
    
    def get_response(self, query:str = None):
        if (self.calls_this_min >= 2):
            api_key_idx += 1
            api_key_idx = api_key_idx % len(self.api_keys)
            self.calls_this_min = 0
        self.calls_this_min += 1
            
        # Make the LLM request.
        request = self._build_request(query)
        response = ""
        response = self.chat.send_message(request)
        return response

    def _delete_frames(self):
        if (self.verbose):
            print(f'Deleting {len(self.frames)} images. This might take a bit...')
        for frame in self.frames:
            print("here")
            genai.delete_file(frame.response.name)
            print('here2')
            if (self.verbose):
                print(f'Deleted {frame.file_path} at URI {frame.response.uri}')
        if (self.verbose):
            print(f"Completed deleting files!\n\nDeleted: {len(self.frames)} files")

    def __del__(self):
        self._delete_frames()


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
    blurred_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0, borderType=cv2.BORDER_REPLICATE)
    return blurred_image

def analyze_distance_gemini(image):
    # Define the prompt for Gemini
    prompt = "Analyze this image and determine the distance of the person from the screen."

    # Convert the image to a format that Gemini can process (e.g., base64)
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')

    # Send the prompt and image to Gemini for analysis
    response = gemini_api.analyze_image(prompt, image_base64)

    # Extract the distance value from the response
    distance = response.get('distance', None)
    if distance is None:
        raise ValueError("Failed to get distance from Gemini response")

    return distance


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
    app.run(port=8000, debug=True)