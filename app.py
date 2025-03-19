from flask import Flask, request, jsonify, send_file
from weasyprint import HTML
import os
import uuid
from functools import wraps  # ✅ Fix: Required for decorator

app = Flask(__name__)

# Directory for saving PDFs
SAVE_DIR = "pdfs"
os.makedirs(SAVE_DIR, exist_ok=True)

# Dummy API keys (Replace with database validation)
API_KEYS = {"test_key_123": "FreeUser"}

# Base URL for accessing files (Change "http://yourdomain.com" when deployed)
BASE_URL = "http://localhost:5000"  # ✅ Fix: Use actual domain in production

def require_api_key(func):
    @wraps(func)  # ✅ Fix: Preserve route functionality
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")
        if api_key not in API_KEYS:
            return jsonify({"error": "Invalid API key"}), 403
        return func(*args, **kwargs)
    return wrapper

@app.route('/generate-pdf', methods=['POST'])
@require_api_key  # Protect the route
def generate_pdf():
    try:
        # Get HTML content from request
        data = request.json
        html_content = data.get("html", "<h1>Empty PDF</h1>")
        
        # Generate unique filename
        file_id = str(uuid.uuid4()) + ".pdf"
        file_path = os.path.join(SAVE_DIR, file_id)
        
        # Convert HTML to PDF
        HTML(string=html_content).write_pdf(file_path)
        
        # ✅ Fix: Return full URL for downloading the PDF
        return jsonify({
            "message": "PDF generated",
            "pdf_url": f"{BASE_URL}/download/{file_id}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<file_id>', methods=['GET'])
def download_pdf(file_id):
    file_path = os.path.join(SAVE_DIR, file_id)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    # ✅ Fix: Host API on all network interfaces (0.0.0.0) for production
    app.run(host="0.0.0.0", port=5000)
