import os
from quart import Quart, request, jsonify
from quart_cors import cors
import google.generativeai as genai
import asyncio

class File:
    def __init__(self, file_path: str, timestamp: str, display_name: str = None):
        self.file_path = file_path
        if display_name:
            self.display_name = display_name
        self.timestamp = timestamp
    def set_response(self, response):
       self.response = response

app = Quart(__name__)
app = cors(app, allow_origin="*")  # Enable CORS to allow requests from your React frontend

UPLOAD_FOLDER = 'uploads/'
PROCESSED_FOLDER = 'processed/'  # To save processed images if needed

# Configure Gemini API
genai.configure(api_key=os.environ["API_KEY"])

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

class VideoGemini:
    def __init__(self, verbose: bool = False, delete: bool = False):
        self.model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
        self.frames = []
        self.verbose = verbose
        self.delete = delete
        self.chat = self.model.start_chat(history=[])

    def upload_frame(self, file: File):
        if self.verbose:
            print(file.file_path)
            print(f'Uploading: {file.file_path}...')
        response = genai.upload_file(path=file.file_path)
        file.set_response(response)
        if self.verbose:
            print(f"Completed file upload")
            if self.delete:
                print(f"Deleting local file at {file.file_path}")
        if self.delete:
            os.remove(file.file_path)
            file.file_path = ""
        self.frames.append(file)

    def _build_request(self, query: str = None):
        request = []
        if query:
            request.append(query)
        for frame in self.frames:
            request.append(frame.timestamp)
            request.append(frame.response)
        return request
    
    async def get_response_async(self, query: str = None):
        request = self._build_request(query)
        response = await self.chat.send_message_async(request)
        return response.text

@app.route('/upload', methods=['POST'])
async def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    upload_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(upload_path)

        # Process the file with Gemini API
        video_gemini = VideoGemini(verbose=True)
        uploaded_file = File(file_path=upload_path)
        video_gemini.upload_frame(uploaded_file)

        # Get the response asynchronously
        prompt = "your_specific_prompt"  # Replace with your actual prompt
        processed_data = await video_gemini.get_response_async(query=prompt)

        # Save processed image if needed (optional)
        processed_filename = os.path.join(PROCESSED_FOLDER, file.filename)
        with open(processed_filename, 'w') as processed_file:
            processed_file.write(processed_data)

        return jsonify({"message": "File uploaded and processed successfully", "response": processed_data}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save and process file: {e}"}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)