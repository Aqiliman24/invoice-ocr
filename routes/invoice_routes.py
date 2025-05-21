from flask import Blueprint, request, jsonify
from controllers.invoice_controller import extract_invoice_total

# Create a Blueprint for invoice routes
invoice_bp = Blueprint('invoice_bp', __name__)

@invoice_bp.route('/extract-total', methods=['POST'])
def extract_total():
    """
    Endpoint to extract total amount from invoice
    Accepts PDF, PNG, JPG, or JPEG files
    Returns the extracted total amount in JSON format
    """
    # Check if file is present in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({'error': 'Empty file provided'}), 400
    
    try:
        # Process the file and extract total amount
        result = extract_invoice_total(file, mode="file")
        return jsonify(result)
    except Exception as e:
        import traceback
        print("Exception in /extract-total:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
