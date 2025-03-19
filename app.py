from flask import Flask, request, jsonify, send_file
from weasyprint import HTML
import os
import uuid

app = Flask(__name__)

# Directory for saving PDFs
SAVE_DIR = "pdfs"
os.makedirs(SAVE_DIR, exist_ok=True)

# Dummy API keys (replace with database validation)
API_KEYS = {"test_key_123": "FreeUser"}

def require_api_key(func):
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
        
        # Get request host dynamically inside the request context
        pdf_url = f"{request.host_url}download/{file_id}"
        
        return jsonify({"message": "PDF generated", "pdf_url": pdf_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<file_id>', methods=['GET'])
def download_pdf(file_id):
    file_path = os.path.join(SAVE_DIR, file_id)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
