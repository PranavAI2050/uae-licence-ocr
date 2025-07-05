import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
API_KEY = os.environ.get('GEMINI_AI_API_KEY')
if not API_KEY:
    raise ValueError("GEMINI_AI_API_KEY not set in environment")
genai.configure(api_key=API_KEY)

def prep_image(image_path):
    sample_file = genai.upload_file(path=image_path, display_name=os.path.basename(image_path))
    return sample_file

def extract_text_from_image(image_file, prompt):
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")
    response = model.generate_content([image_file, prompt])
    return response.text

@app.route('/api/extract', methods=['POST'])
def extract_text():
    if 'image' not in request.files or 'prompt' not in request.form:
        return jsonify({"error": "Missing image or prompt"}), 400

    image = request.files['image']
    prompt = request.form['prompt']

    temp_path = os.path.join("/tmp", image.filename)
    image.save(temp_path)

    try:
        uploaded_image = prep_image(temp_path)
        result_text = extract_text_from_image(uploaded_image, prompt)
        return jsonify({"result": result_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "API is running"}), 200
