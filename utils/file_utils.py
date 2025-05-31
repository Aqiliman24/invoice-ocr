import os
import base64
import tempfile
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

def convert_to_base64(file, page_range=None):
    """
    Convert the uploaded file to base64 encoded images
    
    Args:
        file: The uploaded file object
        page_range: Tuple of (first_page, last_page) or None for single page
        
    Returns:
        list: List of dicts with 'page' and 'image' data
        
    Raises:
        ValueError: If file conversion fails
    """
    filename = file.filename.lower() if hasattr(file, 'filename') else 'unknown'
    
    try:
        if filename.endswith('.pdf'):
            if page_range and len(page_range) == 2:
                return _process_pdf(file, first_page=page_range[0], last_page=page_range[1])
            return _process_pdf(file)
        else:
            # For single image files, wrap in the same format
            return [{
                'page': 1,
                'image': _process_image(file)
            }]
    except Exception as e:
        raise ValueError(f"Error converting file to base64: {str(e)}")

def get_pdf_page_count(file):
    """
    Get the total number of pages in a PDF file
    
    Args:
        file: The PDF file object
        
    Returns:
        int: Total number of pages
    """
    original_position = file.tell()
    
    try:
        # Create a temporary file to read the PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            temp_path = tmp.name
            file_content = file.read()
            tmp.write(file_content)
            tmp.flush()
        
        # Get page count
        with open(temp_path, 'rb') as f:
            return len(PyPDF2.PdfReader(f).pages)
    finally:
        # Clean up and reset file position
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        file.seek(original_position)

def _process_pdf(file, first_page=1, last_page=None):
    """
    Process a PDF file by converting specified pages to images
    
    Args:
        file: The PDF file object
        first_page: First page to process (1-based)
        last_page: Last page to process (inclusive), None for single page
        
    Returns:
        list: List of dicts with 'page' number and 'image' data
    """
    original_position = file.tell()
    temp_path = None
    
    try:
        # Create a temporary file to work with
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            temp_path = tmp.name
            file_content = file.read()
            tmp.write(file_content)
            tmp.flush()
            
        # Get total pages to validate page range
        with open(temp_path, 'rb') as f:
            total_pages = len(PyPDF2.PdfReader(f).pages)
            
        # Validate and adjust page range
        first_page = max(1, min(first_page, total_pages))
        if last_page is None:
            last_page = first_page
        else:
            last_page = min(last_page, total_pages)
            
        try:
            # Convert the specified pages of the PDF to images
            images = pdf2image.convert_from_path(
                temp_path, 
                first_page=first_page,
                last_page=last_page,
                dpi=200,
                fmt='jpeg',
                poppler_path='/usr/bin'
            )
            
            if not images:
                raise ValueError("PDF conversion returned no images")
        except Exception as e:
            print(f"PDF conversion error - File size: {len(file_content)} bytes, Pages: {total_pages}, Error: {str(e)}")
            raise ValueError(f"Failed to convert PDF: {str(e)}")
            
        # Convert images to base64
        results = []
        for i, image in enumerate(images):
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            results.append({
                'page': first_page + i,
                'image': img_str
            })
            
        return results
    finally:
        # Clean up temporary file and reset file position
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        file.seek(original_position)

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
