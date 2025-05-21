import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GPT_MODEL = "gpt-4o"
MAX_TOKENS = 100

# System prompt for invoice total extraction
INVOICE_SYSTEM_PROMPT = (
   """Extract the total amount from this invoice. Determine if the main content 
   (such as totals, items, and vendor details) is handwritten. Ignore signatures, stamps, or small handwritten notes. 
   Respond in JSON: {\"total_amount\": ..., \"handwriting\": ...}"""
)
