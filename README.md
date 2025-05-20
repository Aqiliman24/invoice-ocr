# Invoice Extractor API

A Flask-based backend API that extracts the total amount from invoice files using OpenAI's GPT-4o with vision capabilities.

## Features

- Accepts invoice files via POST (PDF, PNG, JPG, JPEG)
- Extracts total amount using GPT-4o
- Returns the extracted total amount in JSON format

## Setup

### Prerequisites

- Python 3.7+
- For PDF processing on Linux, install poppler-utils:
  ```
  sudo apt-get install poppler-utils
  ```

### Installation

1. Clone the repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. create enviroment variables:
   ```
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```   
5. run the app:
   ```
   python app.py
   ```

## Usage

1. The server will run on http://localhost:5050

## API Endpoints

### Extract Invoice Total

```
POST /extract-total
```

**Request:**
- Content-Type: multipart/form-data
- Body: file - The invoice file (PDF, PNG, JPG, or JPEG)

**Response:**
```json
{
  "total_amount": "$123.45"
}
```

## Example

```bash
curl -X POST http://localhost:5050/extract-total -F "file=@invoice.pdf"
```

## Project Structure

```
invoice-ocr/
├── app.py              # Main entry file
├── routes/             # Route definitions
│   └── invoice_routes.py
├── controllers/        # Request handling logic
│   └── invoice_controller.py
├── services/           # GPT-related logic
│   └── gpt_service.py
├── utils/              # File and image handling
│   └── file_utils.py
├── requirements.txt    # Dependencies
└── .env                # Environment variables (not in repository)
```
## Docker run 

```
docker build -t invoice-extractor .
docker run --env-file .env -p 5050:5050 invoice-extractor
```