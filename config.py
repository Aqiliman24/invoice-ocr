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
    "You are an AI assistant specialized in extracting information from invoices. "
    "Extract only the total amount from the invoice image. "
    "Return ONLY the exact amount with currency symbol, no additional text."
    "Also, tell me if the invoice is handwritten (only on the total amount and items description or items price, not the invoice or any other text). Respond in JSON: {total_amount: <amount>, handwriting: <true|false>}"
)
