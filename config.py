import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GPT_MODEL = "gpt-4.1-mini"
MAX_TOKENS = 100
 
# System prompt for invoice total extraction
INVOICE_SYSTEM_PROMPT = (
    """
    Extract the total amount from this invoice. Determine if the MAIN CONTENT of the invoice (such as totals, items, and vendor details) is handwritten.
    DO NOT consider signatures, stamps, or small handwritten notes when deciding if the invoice is handwritten.
    If ONLY signatures, stamps, or small notes are handwritten, but the main content is printed or typed, return "handwriting": false.
    Only return "handwriting": true if the main content (totals, items, vendor details) is handwritten.
    Respond in JSON: {\"total_amount\": ..., \"handwriting\": ...}
    """
)
