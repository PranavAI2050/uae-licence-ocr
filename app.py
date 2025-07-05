from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from werkzeug.utils import secure_filename

# 🔐 Set up your Google API Key here or from environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)

# Gemini model setup
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# 📤 Upload image to Gemini
def prep_image(image_path):
    sample_file = genai.upload_file(path=image_path, display_name="Driving License")
    return sample_file

# 🧠 Prompt Gemini to extract only the required fields
def extract_license_fields(image_file):
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

    response = model.generate_content([image_file, prompt])
    return response.text

# 📡 API endpoint
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
        sample_file = prep_image(filepath)
        extracted = extract_license_fields(sample_file)
        return jsonify({"extracted_fields": extracted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🏁 Run app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use PORT env var if provided
    app.run(host='0.0.0.0', port=port, debug=True)

