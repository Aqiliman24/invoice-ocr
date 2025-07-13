import fitz  # PyMuPDF
from PIL import Image
import io
import json
import time
from utils.file_utils import convert_to_base64, get_pdf_page_count, allowed_file
from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL, MAX_TOKENS

DO_SYSTEM_PROMPT = """You are an expert at analyzing Delivery Order (DO) documents. Your task is to:
1. Extract the DO Number from the image
2. Check if there is a handwritten signature on the document

Respond in JSON format with two fields:
{"do_id": "extracted_number", "signature": true_or_false}

For DO Number:
- Include all numbers and dashes exactly as shown
- Remove any 'DO' or 'DO Number' prefix
- Return null if no DO number is found

For signature:
- Return true if you see a handwritten signature
- Return false if no signature is found or if it's a digital/stamp signature"""

def extract_do_with_gpt(images_data, system_prompt=None, max_retries=2):
    """
    Extract DO number and check signature using GPT-4 Vision with retry logic
    
    Args:
        images_data: List of dicts with 'page' and 'image' keys
        system_prompt: Optional system prompt override
        max_retries: Number of retry attempts
        
    Returns:
        tuple: (do_id, has_signature)
    """
    if not images_data:
        raise ValueError("No image data provided")
        
    if system_prompt is None:
        system_prompt = DO_SYSTEM_PROMPT

    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Prepare image contents
    image_contents = []
    for idx, img_data in enumerate(images_data, 1):
        image_contents.extend([
            {
                "type": "text",
                "text": f"PAGE {idx} of {len(images_data)}"
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_data['image']}"}
            }
        ])
    
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this document and extract the DO number and check for signature."},
                *image_contents
            ]
        }
    ]

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=messages,
                max_tokens=MAX_TOKENS,
                response_format={"type": "json_object"},
                temperature=0
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return (result.get('do_id'), result.get('signature', False))
            
        except Exception as e:
            if attempt == max_retries:
                raise Exception(f"Failed after {max_retries} attempts: {str(e)}")
            time.sleep(1)

def process_do(file):
    """
    Process a DO document to extract DO number and check signature
    
    Args:
        file: The uploaded file object
        
    Returns:
        dict: Result containing DO ID and signature status
    """
    allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg'}
    
    if not allowed_file(file.filename, allowed_extensions):
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
    
    def reset_file():
        if hasattr(file, 'seek'):
            file.seek(0)
    
    try:
        # Convert file to base64 images
        reset_file()
        images = convert_to_base64(file)
        
        # Extract with GPT
        do_id, has_signature = extract_do_with_gpt(
            images_data=images,
            max_retries=2
        )
        
        # Reset file for potential future use
        reset_file()
        
        return {
            'do_id': do_id,
            'signature': has_signature
        }
        
    except Exception as e:
        print(f"Processing failed: {str(e)}")
        reset_file()  # Reset file even on error
        return {
            'do_id': None,
            'signature': False
        }
