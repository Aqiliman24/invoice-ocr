from openai import OpenAI
import json
from config import OPENAI_API_KEY, GPT_MODEL, MAX_TOKENS, INVOICE_SYSTEM_PROMPT

def extract_total_with_gpt(base64_image):
    """
    Extracts the total amount and detects handwriting from an invoice image using OpenAI's GPT-4o or GPT-4 Turbo vision model.
    Only supports base64 image input.
    Args:
        base64_image: Base64-encoded image data
    Returns:
        tuple: (total_amount_value, handwriting_value)
    Raises:
        Exception: If API call fails or extraction is unsuccessful
    """
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")
    client = OpenAI(api_key=OPENAI_API_KEY)
    system_prompt = INVOICE_SYSTEM_PROMPT
    try:
        image_content = {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        }
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract the total amount and tell me if this invoice is handwritten. Respond in JSON."},
                        image_content
                    ]
                }
            ],
            max_tokens=MAX_TOKENS
        )
        content = response.choices[0].message.content.strip()
        try:
            result = json.loads(content)
            total = result.get("total_amount")
            handwriting = result.get("handwriting")
            return total, handwriting
        except Exception:
            # Try to handle markdown-wrapped JSON
            if content.startswith("```") and content.endswith("```"):
                content_clean = content.strip('`').split('\n', 1)[-1].rsplit('\n', 1)[0]
                try:
                    result = json.loads(content_clean)
                    total = result.get("total_amount")
                    handwriting = result.get("handwriting")
                    return total, handwriting
                except Exception:
                    pass
            # fallback: try to extract total as plain text
            if not any(char.isdigit() for char in content):
                raise ValueError("Failed to extract a valid total amount or parse JSON")
            return content, None
    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}")
