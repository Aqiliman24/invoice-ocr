from services.invoice_service import extract_total_with_gpt
from utils.file_utils import validate_file, convert_to_base64
from werkzeug.utils import secure_filename

def extract_invoice_total(file, mode="base64"):
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
        total_amount, handwriting = extract_total_with_gpt(base64_image)
        # Parse total_amount to float if possible
        if isinstance(total_amount, str):
            import re
            match = re.search(r"([\d,.]+)", total_amount.replace(',', ''))
            if match:
                try:
                    total_amount_value = round(float(match.group(1)), 2)
                except Exception:
                    total_amount_value = total_amount
            else:
                total_amount_value = total_amount
        else:
            total_amount_value = total_amount
        return {
            "handwriting": handwriting,
            "total_amount": total_amount_value
        }
    except Exception as e:
        raise ValueError(f"Error processing invoice: {str(e)}")
