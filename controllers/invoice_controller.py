from services.gpt_service import extract_total_with_gpt
from utils.file_utils import validate_file, convert_to_base64
from werkzeug.utils import secure_filename
import os

def extract_invoice_total(file):
    """
    Process the uploaded invoice file and extract the total amount
    
    Args:
        file: The uploaded file object from the request
        
    Returns:
        dict: A dictionary containing the extracted total amount
        
    Raises:
        ValueError: If the file is invalid or processing fails
    """
    # Validate file type
    filename = secure_filename(file.filename)
    if not validate_file(filename):
        raise ValueError(f"Invalid file format. Supported formats: PDF, PNG, JPG, JPEG")
    
    try:
        # Convert file to base64 (handles both images and PDFs)
        base64_image = convert_to_base64(file)
        
        # Extract total amount and handwriting flag using GPT-4o
        result = extract_total_with_gpt(base64_image)
        # result is a dict: {"total_amount": ..., "handwriting": ...}
        return result
    except Exception as e:
        raise ValueError(f"Error processing invoice: {str(e)}")
