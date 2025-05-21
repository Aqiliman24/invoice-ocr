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
  "total_amount": "$123.45",
  "handwriting": false
}
```
- `total_amount`: The extracted total amount (with currency symbol)
- `handwriting`: Whether the invoice total/items are handwritten (`true` or `false`)


## Example

```bash
curl -X POST http://localhost:5050/extract-total -F "file=@invoice.pdf"
```

## Batch Testing & Reporting

Use `test_report.py` to run batch extraction and generate a visual HTML report:

```bash
python test_report.py --claims-dir claims --num 5
```
- The report will show the total, time taken, and whether each invoice is handwritten.

## Project Structure

```
invoice-ocr/
├── app.py              # Main entry file
├── routes/             # Route definitions
│   └── invoice_routes.py
├── controllers/        # Request handling logic
│   └── invoice_controller.py
├── services/           # Invoice extraction logic
│   └── invoice_service.py
├── utils/              # File and image handling
│   └── file_utils.py
├── requirements.txt    # Dependencies
├── .env                # Environment variables (not in repository)
├── .gitignore          # Git ignore rules
├── .dockerignore       # Docker build ignore rules
└── .env                # Environment variables (not in repository)
```
## Docker run 

```
docker build -t invoice-extractor .
docker run --env-file .env -p 5050:5050 invoice-extractor
```

## Environment & Troubleshooting

- **.env**: Store your OpenAI API key and config here (never commit to git!).
- **.gitignore**: Ensures sensitive files and venv are not tracked.
- **.dockerignore**: Prevents venv, .env, and OS files from being copied into Docker image.

### Common Issues
- If you see errors about OpenAI API or 'proxies', ensure you have only `openai>=1.12.0` installed and that your Docker image is rebuilt with `--no-cache` after any requirements or code changes.
- For PDF support, make sure `poppler-utils` is installed on your system (Linux).

## Changelog
- API now returns a `handwriting` flag (boolean) for each invoice.
- `test_report.py` displays the handwriting flag in the HTML report.
