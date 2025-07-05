import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
API_KEY = os.environ.get('GOOGLE_API_KEY')
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not set in environment")
genai.configure(api_key=API_KEY)

# Fixed prompt for driving license parsing
PROMPT = """
You are a document parser. Analyze this driving license image and extract the following fields only:

Return the result as **valid JSON** with these exact keys:
{
  "full_name": "...",
  "license_number": "...",
  "date_of_birth": "...",
  "nationality": "...",
  "license_expiry_date": "...",
  "license_issue_date": "...",
  "place_of_issue": "..."
}

⚠️ If any value is missing or unreadable due to blur, occlusion, or noise, return: "failed to get" as the value for that field.

Don't include any explanation. Only return the JSON object.
"""

def prep_image(image_path):
    sample_file = genai.upload_file(path=image_path, display_name=os.path.basename(image_path))
    return sample_file

def extract_text_from_image(image_file):
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")
    response = model.generate_content([image_file, PROMPT])
    return response.text

@app.route('/api/extract', methods=['POST'])
def extract_text():
    if 'image' not in request.files:
        return jsonify({"error": "Missing image"}), 400

    image = request.files['image']
    temp_path = os.path.join("/tmp", image.filename)
    image.save(temp_path)

    try:
        uploaded_image = prep_image(temp_path)
        result_text = extract_text_from_image(uploaded_image)
        return jsonify({"result": result_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "API is running"}), 200
