import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GPT_MODEL = "gpt-4.1-mini"
MAX_TOKENS = 300
 
# System prompt for invoice total, date, and bill to validation
INVOICE_SYSTEM_PROMPT = (
    """
    Extract information from this invoice with special attention to finding the correct total amount. Follow these rules carefully:

    1. For the total amount:
       - CRITICAL: Follow these steps IN ORDER:
         a. First, check if this is a single-page or multi-page invoice
         b. For SINGLE-PAGE invoices:
            * Look for the FINAL amount at the bottom of the page
            * Common labels: "Total", "Total Amount", "Net Amount", "Amount Due"
            * This will typically be the last and largest amount on the page
         c. For MULTI-PAGE invoices:
            * Go to the LAST PAGE
            * Look for "TOTAL BILL AMOUNT" or "TOTAL AMOUNT TO BE PAID"
            * This amount will be larger than any subtotals from previous pages

       - VALIDATION CHECKLIST (Must pass ALL):
         1. Is this amount at or near the bottom of the page? ✓
         2. Is it labeled as a final total (not a subtotal)? ✓
         3. Is it the largest amount on the invoice? ✓
         4. Does it make sense as a sum of the line items? ✓

    2. For the date:
       - Look for fields labeled "Bill Date", "Print Date", or "Invoice Date"
       - IMPORTANT: Convert DD/MM/YYYY format to YYYY-MM-DD format
       - Example: "11/07/2025" should become "2025-07-11"
       - If multiple dates exist, prioritize the Bill Date
       - If only month and year are provided (e.g. "April 2025" or "04/2025"), use the first day of that month (e.g. "2025-04-01")

    3. For handwriting validation:
       - DO NOT consider signatures, stamps, or small handwritten notes
       - If ONLY signatures, stamps, or small notes are handwritten, but the main content is printed or typed, return "handwriting": false
       - Only return "handwriting": true if the main content (totals, items, vendor details) is handwritten

    4. For bill to validation:
       - Look for "bill to", "billed to", "customer", "client", or similar fields
       - Check if the company name matches "MEDKAD SDN BHD" (case insensitive)
       - Return true if matches "MEDKAD SDN BHD" (ignoring case)
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
