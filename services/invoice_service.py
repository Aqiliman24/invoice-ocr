from openai import OpenAI
import json
from config import OPENAI_API_KEY, GPT_MODEL, MAX_TOKENS, INVOICE_SYSTEM_PROMPT
import time
from utils.file_utils import convert_to_base64, get_pdf_page_count

def extract_total_with_gpt(images_data, system_prompt=None, max_retries=2):
    """
    Extract total amount from invoice using GPT-4 Vision with retry logic
    
    Args:
        images_data: List of dicts with 'page' and 'image' keys
        system_prompt: Optional system prompt override
        max_retries: Number of retry attempts
        
    Returns:
        tuple: (total_amount, handwriting)
    """
    if not images_data:
        raise ValueError("No image data provided")
        
    if system_prompt is None:
        system_prompt = INVOICE_SYSTEM_PROMPT

    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Prepare image contents with page numbers
    image_contents = []
    for img_data in images_data:
        image_contents.append({
            "type": "text",
            "text": f"PAGE {img_data['page']} of {images_data[-1]['page']}"
        })
        image_contents.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_data['image']}"}
        })
    
    # Try multiple times in case of API failures
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": system_prompt
                            },
                            *image_contents
                        ]
                    }
                ],
                max_tokens=MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            total = result.get('total_amount')
            date = result.get('date')
            handwriting = result.get('handwriting', False)
            return total, date, handwriting
            
        except Exception as e:
            if attempt == max_retries:
                raise Exception(f"Failed after {max_retries} attempts: {str(e)}")
            time.sleep(1)  # Wait before retry

def process_invoice(file, initial_pages=1, fallback_pages=3, prioritize_last_page=False):
    """
    Process an invoice with a two-step approach, optionally prioritizing the last page
    
    Args:
        file: The uploaded file object
        initial_pages: Number of pages to try first (default: 1)
        fallback_pages: Number of pages to try if first attempt fails (default: 3)
        prioritize_last_page: If True, process last page first (default: False)
        
    Returns:
        tuple: (total_amount, handwriting)
    """
    def reset_file():
        if hasattr(file, 'seek'):
            file.seek(0)
    
    # If we're prioritizing the last page and it's a PDF
    if prioritize_last_page and hasattr(file, 'filename') and file.filename.lower().endswith('.pdf'):
        try:
            # Get total pages
            total_pages = get_pdf_page_count(file)
            
            # If we have a PDF with multiple pages, process the last page first
            if total_pages > 1:
                reset_file()
                try:
                    # Try just the last page
                    page_images = convert_to_base64(file)
                    total_amount, date, handwriting = extract_total_with_gpt(
                        images_data=page_images,
                        max_retries=1
                    )
                    
                    if total_amount is not None:
                        return total_amount, date, handwriting
                except Exception as e:
                    print(f"Last page attempt failed: {str(e)}")
                    reset_file()
        except Exception as e:
            print(f"Error processing last page first: {str(e)}")
            reset_file()
    
    # Try first page
    try:
        reset_file()
        first_page_images = convert_to_base64(file, page_range=(1, 1))
        
        # Extract with GPT
        total_amount, date, handwriting = extract_total_with_gpt(
            images_data=first_page_images,
            max_retries=1
        )
        
        # If we got a valid amount, return it
        if total_amount is not None and total_amount != "N/A":
            return total_amount, date, handwriting
    except Exception as e:
        print(f"First page attempt failed: {str(e)}")
        reset_file()

    # If first page didn't have total, check if it's a PDF with multiple pages
    if hasattr(file, 'filename') and file.filename.lower().endswith('.pdf'):
        try:
            total_pages = get_pdf_page_count(file)
            if total_pages > 1:
                reset_file()
                # Try the last page
                last_page_images = convert_to_base64(file, page_range=(total_pages, total_pages))
                total_amount, date, handwriting = extract_total_with_gpt(
                    images_data=last_page_images,
                    max_retries=1
                )
                if total_amount is not None and total_amount != "N/A":
                    return total_amount, date, handwriting
        except Exception as e:
            print(f"Last page attempt failed: {str(e)}")
            reset_file()
    
    # If both first and last page failed, try with more pages as fallback
    if fallback_pages > initial_pages:
        try:
            reset_file()
            page_images = convert_to_base64(file, page_range=(1, fallback_pages))
            total_amount, date, handwriting = extract_total_with_gpt(
                images_data=page_images,
                max_retries=2
            )
            if total_amount is not None and total_amount != "N/A":
                return total_amount, date, handwriting
        except Exception as e:
            print(f"Fallback attempt failed: {str(e)}")
            reset_file()
    
    # Return None for total_amount if no valid amount found
    return None, date, handwriting
