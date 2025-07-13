from flask import Flask, jsonify
from routes.invoice_routes import invoice_bp
from routes.do_routes import do_bp
import os
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Check if OpenAI API key is set
if not os.environ.get('OPENAI_API_KEY'):
    print("Warning: OPENAI_API_KEY environment variable is not set")

app = Flask(__name__)

# Register blueprints
app.register_blueprint(invoice_bp)
app.register_blueprint(do_bp)

# Add health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

# Configure app for production
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

if __name__ == '__main__':
    # Only used for development
    app.run(host="0.0.0.0", port=5050, debug=False)