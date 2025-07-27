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
        tuple: (total_amount, date, handwriting, bill_to)
    """
    if not images_data:
        raise ValueError("No image data provided")
        
    if system_prompt is None:
        system_prompt = INVOICE_SYSTEM_PROMPT

    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Prepare image contents with page numbers - optimized to reduce string operations
    total_pages = images_data[-1]['page']
    image_contents = []
    for img_data in images_data:
        # Combine text and image in one append to reduce list operations
        image_contents.extend([
            {
                "type": "text",
                "text": f"PAGE {img_data['page']} of {total_pages}"
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_data['image']}"}
            }
        ])
    
    # Prepare message once to avoid rebuilding on retries
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": system_prompt},
                *image_contents
            ]
        }
    ]

    # Try multiple times in case of API failures
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=messages,
                max_tokens=MAX_TOKENS,
                response_format={"type": "json_object"},
                temperature=0  # Reduce randomness for faster processing
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return (
                result.get('total_amount'),
                result.get('date'),
                result.get('handwriting', False),
                result.get('bill_to', False)
            )
            
        except Exception as e:
            if attempt == max_retries:
                raise Exception(f"Failed after {max_retries} attempts: {str(e)}")
            time.sleep(1)  # Wait before retry

def process_invoice(file, initial_pages=1, fallback_pages=3):
    """
    Process an invoice, handling both single and multi-page formats
    
    Args:
        file: The uploaded file object
        initial_pages: Number of pages to try if first attempt fails (default: 1)
        fallback_pages: Number of pages to try if other attempts fail (default: 3)
        
    Returns:
        tuple: (total_amount, date, handwriting, bill_to)
    """
    # Initialize variables with default values
    date = None
    handwriting = False
    bill_to = False
    
    def reset_file():
        if hasattr(file, 'seek'):
            file.seek(0)
    
    # Check if it's a PDF file
    is_pdf = hasattr(file, 'filename') and file.filename.lower().endswith('.pdf')
    
    if is_pdf:
        try:
            # Get total pages
            total_pages = get_pdf_page_count(file)
            
            # For single-page PDFs, process the only page
            if total_pages == 1:
                reset_file()
                page_images = convert_to_base64(file, page_range=(1, 1))
                result = extract_total_with_gpt(
                    images_data=page_images,
                    max_retries=2
                )
                if result[0] is not None and result[0] != "N/A":
                    return result
            
            # For multi-page PDFs, always check the last page first
            elif total_pages > 1:
                reset_file()
                try:
                    # Try just the last page
                    page_images = convert_to_base64(file, page_range=(total_pages, total_pages))
                    result = extract_total_with_gpt(
                        images_data=page_images,
                        max_retries=2
                    )
                    if result[0] is not None and result[0] != "N/A":
                        return result
                except Exception as e:
                    print(f"Last page attempt failed: {str(e)}")
                    reset_file()
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            reset_file()
    
    # For non-PDFs or if PDF processing failed, try first page
    try:
        reset_file()
        first_page_images = convert_to_base64(file, page_range=(1, 1))
        result = extract_total_with_gpt(
            images_data=first_page_images,
            max_retries=2
        )
        if result[0] is not None and result[0] != "N/A":
            return result
    except Exception as e:
        print(f"First page attempt failed: {str(e)}")
        reset_file()
    
    # If first page didn't work, try last page for PDFs
    if hasattr(file, 'filename') and file.filename.lower().endswith('.pdf'):
        try:
            reset_file()
            total_pages = get_pdf_page_count(file)
            if total_pages > 0:
                # Always try the last page first for PDFs
                last_page_images = convert_to_base64(file, page_range=(total_pages, total_pages))
                result = extract_total_with_gpt(
                    images_data=last_page_images,
                    max_retries=2  # Increased retries for better reliability
                )
                if result[0] is not None and result[0] != "N/A":  # Check total_amount
                    return result
        except Exception as e:
            print(f"Last page attempt failed: {str(e)}")
            reset_file()

    # If both first and last page failed, try with more pages as fallback
    if fallback_pages > initial_pages:
        try:
            reset_file()
            page_images = convert_to_base64(file, page_range=(1, fallback_pages))
            result = extract_total_with_gpt(
                images_data=page_images,
                max_retries=2
            )
            if result[0] is not None and result[0] != "N/A":  # Check total_amount
                return result
        except Exception as e:
            print(f"Fallback attempt failed: {str(e)}")
            reset_file()
    
    # Return None for total_amount if no valid amount found
    return (None, date, handwriting, bill_to)
