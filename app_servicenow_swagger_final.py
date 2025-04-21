from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import uuid
import subprocess
from flasgger import Swagger, swag_from

app = Flask(__name__)
CORS(app)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: rule.rule.startswith('/convert/docx/to/pdf/swagger'),
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger_template = {
    "info": {
        "title": "DOCX to PDF Converter API1",
        "description": """1Use this endpoint to upload a DOCX file and receive a downloadable PDF link.

⚠️ Copy the download_url from the response and paste it in a new browser tab to download the file.""",
        "version": "1.5.0",
        "contact": {
            "name": "Your Name",
            "email": "your.email@example.com",
            "url": "https://yourcompany.com"
        }
    },
    "host": "127.0.0.1:5000",
    "basePath": "/",
    "schemes": ["http"]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

LIBREOFFICE_PATH = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

def convert_to_pdf(docx_path, pdf_path):
    result = subprocess.run([
        LIBREOFFICE_PATH, "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(pdf_path), docx_path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("LibreOffice STDOUT:", result.stdout.decode())
    print("LibreOffice STDERR:", result.stderr.decode())
    return result.returncode == 0, result.stderr.decode('utf-8') if result.returncode != 0 else None

@app.route('/convert/docx/to/pdf', methods=['POST'])
def convert_docx_to_pdf_servicenow():
    file_id = str(uuid.uuid4())
    docx_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.docx")
    pdf_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.pdf")

    try:
        if not request.data:
            return {"error": "No file data received"}, 400

        with open(docx_path, 'wb') as f:
            f.write(request.data)

        success, error = convert_to_pdf(docx_path, pdf_path)
        if not success:
            return {"error": error}, 500

        return send_file(pdf_path, mimetype='application/pdf', as_attachment=True, download_name="converted.pdf")
    finally:
        if os.path.exists(docx_path):
            os.remove(docx_path)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

@app.route('/convert/docx/to/pdf/swagger', methods=['POST'])
@swag_from({
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'Upload a DOCX file to convert to PDF'
        }
    ],
    'responses': {
        200: {
            'description': 'Returns a download URL as JSON. ⚠️ Copy the URL and paste it into a new browser tab to download the PDF.',
            'examples': {
                'application/json': {
                    "message": "PDF generated successfully",
                    "download_url": "http://127.0.0.1:5000/downloads/<uuid>.pdf"
                }
            }
        },
        400: {'description': 'Missing file'},
        500: {'description': 'Conversion failed'}
    }
})
def convert_docx_to_pdf_swagger():
    file_id = str(uuid.uuid4())
    docx_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.docx")
    pdf_filename = f"{file_id}.pdf"
    pdf_path = os.path.join(DOWNLOAD_FOLDER, pdf_filename)

    try:
        if 'file' not in request.files:
            return {"error": "File is required"}, 400

        file = request.files['file']
        file.save(docx_path)

        success, error = convert_to_pdf(docx_path, pdf_path)
        if not success:
            return {"error": error}, 500

        if os.path.exists(pdf_path):
            return jsonify({
                "message": "PDF generated successfully",
                "download_url": f"http://127.0.0.1:5000/downloads/{pdf_filename}"
            })
        else:
            return {"error": "PDF file not found after conversion"}, 500
    finally:
        if os.path.exists(docx_path):
            os.remove(docx_path)

@app.route('/downloads/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='application/pdf', as_attachment=True)
    else:
        return {"error": "File not found"}, 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
