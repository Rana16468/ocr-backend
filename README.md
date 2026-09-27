# OCR Backend API

A FastAPI-based backend for optical character recognition (OCR), QR code scanning, and barcode scanning. This project is designed to work with a frontend app and return extracted text or scanned data as JSON responses.

## Features

- OCR text extraction using EasyOCR
- QR code detection and decoding
- Barcode scanning support using zxing-cpp
- OpenCV fallback for QR detection
- Cross-origin support for frontend integration via CORS
- Simple REST API endpoints for image upload and processing

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- EasyOCR
- OpenCV
- Pillow
- NumPy
- zxing-cpp

## Project Structure

```text
ocr-backend/
├── main.py
├── README.md
├── .gitignore
└── venv/          # local virtual environment (should be ignored by Git)
```

## Installation

1. Clone the project:

```bash
git clone <your-repository-url>
cd ocr-backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install fastapi uvicorn easyocr pillow zxing-cpp opencv-python-headless numpy
```

## Run the Server

```bash
python -m uvicorn main:app --reload
```

Then open the app at:

```text
http://127.0.0.1:8000
```

## API Endpoints

### GET /

Returns a basic server health message.

### POST /scan

Uploads an image and extracts text using OCR.

Request:
- Form field: `file`
- Type: image file

Response:
```json
{
  "success": true,
  "filename": "sample.png",
  "scanned_data": ["Hello World", "Example text"]
}
```

### POST /scan/qr

Uploads an image and attempts to detect QR codes.

Response:
```json
{
  "success": true,
  "filename": "qr.png",
  "qr_data": ["https://example.com", "ABC123"]
}
```

### POST /scan/barcode

Uploads an image and scans barcodes.

Response:
```json
{
  "success": true,
  "filename": "barcode.png",
  "barcode_data": [
    {
      "code_type": "EAN_13",
      "code_number": "1234567890123"
    }
  ]
}
```

## Notes

- EasyOCR downloads model files on first run; this may take a little time on startup.
- Some native dependencies may require Windows-specific DLL support, especially when using barcode/QR libraries.
- This project is intended for development and local usage unless you configure deployment-specific environment settings.

## License

This project is licensed under the MIT License.

## GitHub Push Command

After creating the repository on GitHub, run:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repository-url>
git push -u origin main
```
