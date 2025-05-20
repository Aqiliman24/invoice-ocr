import os
import base64
from PIL import Image
from io import BytesIO
import pdf2image
import PyPDF2

def validate_file(filename):
    """
    Validate that the file is one of the supported types: PDF, PNG, JPG, or JPEG
    
    Args:
        filename (str): The name of the file to validate
        
    Returns:
        bool: True if the file is valid, False otherwise
    """
    allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def convert_to_base64(file):
    """
    Convert the uploaded file to base64 encoding
    - If PDF, extracts first page and converts to image
    - If image, processes directly
    
    Args:
        file: The uploaded file object
        
    Returns:
        str: Base64-encoded image data
        
    Raises:
        ValueError: If file conversion fails
    """
    filename = file.filename.lower()
    
    try:
        if filename.endswith('.pdf'):
            # For PDF files, extract the first page and convert to image
            return _process_pdf(file)
        else:
            # For image files, process directly
            return _process_image(file)
    except Exception as e:
        raise ValueError(f"Error converting file to base64: {str(e)}")

def _process_pdf(file):
    """
    Process a PDF file by converting its first page to an image and then to base64
    
    Args:
        file: The PDF file object
        
    Returns:
        str: Base64-encoded image data
    """
    # Save the uploaded file temporarily
    temp_path = 'temp_file.pdf'
    file.save(temp_path)
    
    try:
        # Convert the first page of the PDF to an image
        images = pdf2image.convert_from_path(
            temp_path, 
            first_page=1,
            last_page=1
        )
        
        if not images:
            raise ValueError("Failed to extract page from PDF")
        
        # Get the first page image
        image = images[0]
        
        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return img_str
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def _process_image(file):
    """
    Process an image file by converting it to base64
    
    Args:
        file: The image file object
        
    Returns:
        str: Base64-encoded image data
    """
    # Open the image using PIL
    image = Image.open(file)
    
    # Convert image to base64
    buffered = BytesIO()
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return img_str
