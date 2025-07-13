import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GPT_MODEL = "gpt-4.1-mini"
MAX_TOKENS = 150
 
# System prompt for invoice total, date, and bill to validation
INVOICE_SYSTEM_PROMPT = (
    """
    Extract the total amount, date, and validate if the bill to is MEDKAD SDN BHD from this invoice. Determine if the MAIN CONTENT of the invoice (such as totals, items, and vendor details) is handwritten.
    DO NOT consider signatures, stamps, or small handwritten notes when deciding if the invoice is handwritten.
    If ONLY signatures, stamps, or small notes are handwritten, but the main content is printed or typed, return "handwriting": false.
    Only return "handwriting": true if the main content (totals, items, vendor details) is handwritten.
    For the date:
    1. Look for invoice date, bill date, or any similar date field
    2. If only month and year are provided (e.g. "April 2025" or "04/2025"), use the first day of that month (e.g. "2025-04-01")
    3. Convert all dates to YYYY-MM-DD format
    For bill to validation:
    1. Look for "bill to", "billed to", "customer", "client", or similar fields
    2. Check if the company name matches "MEDKAD SDN BHD" (case insensitive)
    3. For the "bill_to" field in the response:
       - Return true if the company name matches "MEDKAD SDN BHD" (ignoring case)
       - Return false for any other company name or if no bill to is found
    Respond in JSON format with these exact fields:
    {
        "total_amount": <number or string>,
        "date": "YYYY-MM-DD",
        "handwriting": <boolean>,
        "bill_to": <boolean>
    }
    """
)
