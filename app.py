from flask import Flask
from routes.invoice_routes import invoice_bp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if OpenAI API key is set
if not os.environ.get('OPENAI_API_KEY'):
    print("Warning: OPENAI_API_KEY environment variable is not set")

app = Flask(__name__)

# Register blueprints
app.register_blueprint(invoice_bp)

if __name__ == '__main__':
    port = 5050
    host = "0.0.0.0"
    app.run(debug=True, port=port, host=host)