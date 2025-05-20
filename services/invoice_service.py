from openai import OpenAI
import json
from config import OPENAI_API_KEY, GPT_MODEL, MAX_TOKENS, INVOICE_SYSTEM_PROMPT

def extract_total_with_gpt(base64_image):
    """
    Extract the total amount from an invoice image using GPT-4o, and detect if handwriting is present.
    
    Args:
        base64_image (str): Base64-encoded image data
    Returns:
        dict: {"total_amount": str, "handwriting": bool}
    Raises:
        Exception: If API call fails or extraction is unsuccessful
    """
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")
    client = OpenAI(api_key=OPENAI_API_KEY)
    try:
        # Ask GPT to extract total and detect handwriting
        system_prompt = INVOICE_SYSTEM_PROMPT
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract the total amount and tell me if this invoice is handwritten. Respond in JSON."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=MAX_TOKENS
        )
        content = response.choices[0].message.content.strip()
        try:
            result = json.loads(content)
            # Validate keys
            if "total_amount" not in result or "handwriting" not in result:
                raise ValueError("Missing keys in GPT response")
            return {
                "total_amount": result["total_amount"],
                "handwriting": bool(result["handwriting"])
            }
        except Exception:
            # fallback: try to extract total as before
            if not any(char.isdigit() for char in content):
                raise ValueError("Failed to extract a valid total amount or parse JSON")
            return {"total_amount": content, "handwriting": None}
    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}")
