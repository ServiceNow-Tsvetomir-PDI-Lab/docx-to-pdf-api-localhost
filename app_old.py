from flask import Flask, request, send_file
import os
import uuid
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists

# Absolute path to LibreOffice binary on macOS
LIBREOFFICE_PATH = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

@app.route('/convert/docx/to/pdf', methods=['POST'])
def convert_docx_to_pdf():
    # Check if the request has the correct Content-Type
    if request.content_type != 'application/octet-stream':
        return {"error": "Invalid Content-Type. Use application/octet-stream"}, 400

    # Ensure file data is present in the request
    if not request.data:
        return {"error": "No file data received"}, 400

    # Verify that LibreOffice is available at the specified path
    if not os.path.exists(LIBREOFFICE_PATH):
        return {"error": f"LibreOffice not found at: {LIBREOFFICE_PATH}"}, 500

    # Generate unique filenames for the DOCX and resulting PDF
    file_id = str(uuid.uuid4())
    docx_filename = f"{file_id}.docx"
    pdf_filename = f"{file_id}.pdf"
    docx_path = os.path.join(UPLOAD_FOLDER, docx_filename)
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)

    try:
        # Save the incoming DOCX data to a file
        with open(docx_path, 'wb') as f:
            f.write(request.data)

        # Convert the DOCX to PDF using LibreOffice in headless mode
        result = subprocess.run([
            LIBREOFFICE_PATH, "--headless", "--convert-to", "pdf", "--outdir", UPLOAD_FOLDER, docx_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Print conversion logs to terminal for debugging
        print("LibreOffice STDOUT:", result.stdout.decode())
        print("LibreOffice STDERR:", result.stderr.decode())

        # If conversion failed, return error message
        if result.returncode != 0:
            return {"error": f"LibreOffice conversion failed: {result.stderr.decode('utf-8')}"}, 500

        # Return the generated PDF file if it exists
        if os.path.exists(pdf_path):
            return send_file(pdf_path, mimetype='application/pdf', as_attachment=True, download_name="converted.pdf")
        else:
            return {"error": "PDF file not found after conversion"}, 500

    except Exception as e:
        # Handle unexpected errors
        return {"error": f"Unexpected server error: {str(e)}"}, 500

    finally:
        # Clean up temporary files
        if os.path.exists(docx_path):
            os.remove(docx_path)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

# Start the Flask development server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
