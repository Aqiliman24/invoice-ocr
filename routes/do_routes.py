from flask import Blueprint, request, jsonify
from controllers.do_controller import DOController

do_bp = Blueprint('do', __name__)
controller = DOController()

@do_bp.route('/extract-do', methods=['POST'])
def extract_do():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty file provided'}), 400

        result = controller.process_do(file)
        return jsonify(result), 200
    except Exception as e:
        import traceback
        print("Exception in /extract-do:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
