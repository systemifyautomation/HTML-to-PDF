"""
HTML to PDF Converter API
A Flask-based REST API for converting HTML content to PDF documents.
"""

from flask import Flask, request, send_file, jsonify
from weasyprint import HTML, CSS
from jinja2 import Template
import io
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint with API documentation.
    """
    return jsonify({
        'service': 'HTML to PDF Converter API',
        'version': '1.0.0',
        'endpoints': {
            '/': 'GET - API documentation',
            '/convert': 'POST - Convert HTML to PDF',
            '/health': 'GET - Health check'
        },
        'usage': {
            'endpoint': '/convert',
            'method': 'POST',
            'content-type': 'application/json',
            'body': {
                'html': 'HTML content as string',
                'css': 'Optional CSS styles as string',
                'filename': 'Optional output filename (default: document.pdf)'
            }
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/convert', methods=['POST'])
def convert_html_to_pdf():
    """
    Convert HTML content to PDF.
    
    Expects JSON payload with:
    - html: HTML content (required)
    - css: CSS styles (optional)
    - filename: Output PDF filename (optional, default: document.pdf)
    
    Returns:
    - PDF file as attachment
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract HTML content
        html_content = data.get('html', '')
        if not html_content:
            return jsonify({'error': 'HTML content is required'}), 400
        
        # Extract optional CSS
        css_content = data.get('css', '')
        
        # Extract optional filename
        filename = data.get('filename', 'document.pdf')
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        logger.info(f"Converting HTML to PDF: {filename}")
        
        # Create PDF from HTML
        pdf_buffer = io.BytesIO()
        
        if css_content:
            # Create HTML with CSS
            html = HTML(string=html_content)
            css = CSS(string=css_content)
            html.write_pdf(pdf_buffer, stylesheets=[css])
        else:
            # Create HTML without additional CSS
            html = HTML(string=html_content)
            html.write_pdf(pdf_buffer)
        
        # Reset buffer position to beginning
        pdf_buffer.seek(0)
        
        logger.info(f"PDF generated successfully: {filename}")
        
        # Return PDF as downloadable file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error converting HTML to PDF: {str(e)}")
        return jsonify({'error': f'Failed to convert HTML to PDF: {str(e)}'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """
    Handle request size too large error.
    """
    return jsonify({'error': 'Request too large. Maximum size is 16MB'}), 413

@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 errors.
    """
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Handle internal server errors.
    """
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting HTML to PDF Converter API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
