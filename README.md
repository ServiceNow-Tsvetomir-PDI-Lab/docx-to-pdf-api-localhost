```markdown
# 📝 DOCX to PDF Converter API

A simple REST API built with Flask and LibreOffice to convert `.docx` documents to `.pdf` format.  
Perfect for integration with platforms like **ServiceNow**, where automatic document conversion is required.

---

## 🚀 Features

- Accepts `.docx` files as binary stream
- Converts to `.pdf` using **LibreOffice in headless mode**
- Returns the converted PDF file as a downloadable attachment
- Can be accessed locally or externally via **ngrok**

---

## 📚 API Documentation

### `POST /convert/docx/to/pdf`

Converts a `.docx` file to `.pdf`.

#### Request

- **Method**: `POST`
- **Content-Type**: `application/octet-stream`
- **Body**: Binary file data (DOCX)

#### Response

- `200 OK` – Returns the converted PDF as a file download
- `400 Bad Request` – Missing file or invalid content type
- `500 Internal Server Error` – Conversion failed or LibreOffice not found

---

### 📬 Example Usage

#### ▶️ Postman

1. Open **Postman**
2. Set method to `POST`
3. URL: `http://localhost:5000/convert/docx/to/pdf` (or your ngrok URL)
4. **Headers** tab:
   - Key: `Content-Type`, Value: `application/octet-stream`
5. **Body** tab:
   - Select `binary`
   - Choose a `.docx` file from your local machine
6. Click **Send** – the response will be a PDF file

#### ▶️ cURL

```bash
curl -X POST http://localhost:5000/convert/docx/to/pdf \
     -H "Content-Type: application/octet-stream" \
     --data-binary "@sample.docx" \
     --output converted.pdf
```

---

## ⚙️ Local Setup Instructions

### 🔧 Prerequisites

- Python 3.7+
- [LibreOffice](https://www.libreoffice.org/download/download/)
- [ngrok](https://ngrok.com/download)
- `brew` (macOS only)

### 📦 Installation Steps

```bash
# Create project folder and navigate into it
mkdir -p ~/my-api-localhost
cd ~/my-api-localhost

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt and install dependencies
echo "Flask" > requirements.txt
pip install -r requirements.txt

# Create uploads folder (optional, will be auto-created)
mkdir uploads

# Start Flask server
python app.py
```

API will now be running at:

```
http://127.0.0.1:5000
```

---

## 🌐 Exposing the API with ngrok

To allow external access (e.g. from ServiceNow or remote Postman):

### 🔌 Step-by-step

1. **Install ngrok** (if not already installed)

```bash
brew install ngrok
```

2. **Authenticate ngrok** (first-time only)

```bash
ngrok config add-authtoken <your_token_here>
```

3. **Start your Flask server locally**

```bash
python app.py
```

4. **Expose your API via ngrok**

```bash
ngrok http http://127.0.0.1:5000
```

You’ll get a public HTTPS forwarding URL like:

```
Forwarding  https://abcd1234.ngrok-free.app -> http://127.0.0.1:5000
```

5. **Use that URL in Postman, ServiceNow, or any external tool**:

```bash
curl -X POST https://abcd1234.ngrok-free.app/convert/docx/to/pdf \
     -H "Content-Type: application/octet-stream" \
     --data-binary "@sample.docx" \
     --output converted.pdf
```

---

## 📌 Notes

- Ensure LibreOffice is installed at:
  ```
  /Applications/LibreOffice.app/Contents/MacOS/soffice
  ```
  If not, update the path in `app.py`.

- Temporary `.docx` and `.pdf` files are auto-deleted after each request.
---

## 🧪 Swagger UI Usage

### `POST /convert/docx/to/pdf/swagger`

This endpoint is optimized for Swagger and browser-based tools. It accepts DOCX files using `multipart/form-data` and returns a JSON response with a link to download the converted PDF.

#### Request

- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Body**: Upload field for `.docx` file

#### Response

- `200 OK` – Returns JSON with a field `download_url` like:
  ```json
  {
    "message": "PDF generated successfully",
    "download_url": "http://127.0.0.1:5000/downloads/<uuid>.pdf"
  }
  ```

  ⚠️ **Important:** Copy the `download_url` value and paste it into a new browser tab to download the PDF.

- `400 Bad Request` – File missing or invalid
- `500 Internal Server Error` – Conversion failed

---

## 🧩 Multi-endpoint Architecture

The application exposes two distinct endpoints for maximum compatibility:

| Endpoint                        | Description                                           | Target Use     |
|---------------------------------|-------------------------------------------------------|----------------|
| `/convert/docx/to/pdf`          | Accepts `application/octet-stream` and returns PDF   | ✅ ServiceNow  |
| `/convert/docx/to/pdf/swagger`  | Accepts file uploads (`multipart/form-data`) and returns `download_url` as JSON | ✅ Swagger / UI / Postman |

This ensures both automation (e.g. ServiceNow) and user interfaces (e.g. Swagger, HTML) are fully supported.

---

## 📘 Swagger UI Access

Once the Flask server is running locally, you can access the Swagger UI here:

```
http://127.0.0.1:5000/docs
```

You’ll find the Swagger-only endpoint available there with file upload support and a clear description about how to download the PDF.
