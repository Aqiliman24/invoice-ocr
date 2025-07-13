from services.invoice_service import process_invoice
from utils.file_utils import allowed_file
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
    # allowed file type
    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        raise ValueError(f"Invalid file format. Supported formats: PDF, PNG, JPG, JPEG")
    
    try:
        # Process the invoice using the service layer
        total_amount, date, handwriting, bill_to = process_invoice(file)
        
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
            "total_amount": total_amount_value,
            "date": date,
            "bill_to": bill_to
        }
    except Exception as e:
        raise ValueError(f"Error processing invoice: {str(e)}")
