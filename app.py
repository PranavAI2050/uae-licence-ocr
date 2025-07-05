from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from werkzeug.utils import secure_filename
from PIL import Image
import base64
import io

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)

# Gemini model setup
model = genai.GenerativeModel("gemini-1.5-flash")  # or gemini-pro-vision

def image_to_base64(image_path):
    with Image.open(image_path) as img:
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        encoded_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return {
            "mime_type": "image/jpeg",
            "data": encoded_string
        }

def extract_license_fields(image_path):
    base64_image = image_to_base64(image_path)

    prompt = """
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

    response = model.generate_content([
        {"mime_type": base64_image["mime_type"], "data": base64_image["data"]},
        prompt
    ])

    return response.text

@app.route('/extract-license', methods=['POST'])
def upload_and_extract():
    if 'file' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join("uploads", filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(filepath)

    try:
        extracted = extract_license_fields(filepath)
        return jsonify({"extracted_fields": extracted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
