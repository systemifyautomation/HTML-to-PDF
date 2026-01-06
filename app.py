"""
HTML to PDF Converter API
A Flask-based REST API for converting HTML content to PDF documents using Puppeteer.
Renders HTML exactly like Chrome browser for perfect compatibility.
"""

__version__ = "2.0.0"
__updated_at__ = "2026-01-05T00:00:00Z"

from flask import Flask, request, send_file, jsonify
from playwright.sync_api import sync_playwright
import base64
import io
import os
import json
import logging
import tempfile
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Rate limiting storage
rate_limit_storage = defaultdict(list)

# API keys file path
API_KEYS_FILE = os.path.join(os.path.dirname(__file__), '.api-keys.json')

# Version file path
VERSION_FILE = os.path.join(os.path.dirname(__file__), 'version.json')

def load_version_info():
    """
    Load version information from version.json file.
    If file doesn't exist, returns default version from __version__.
    """
    if not os.path.exists(VERSION_FILE):
        return {
            'version': __version__,
            'name': 'HTML-to-PDF API',
            'updated_at': __updated_at__,
            'changelog': []
        }
    
    try:
        with open(VERSION_FILE, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.warning(f"Error loading version file: {str(e)}")
        return {
            'version': __version__,
            'name': 'HTML-to-PDF API',
            'updated_at': __updated_at__,
            'changelog': []
        }

# Load API keys from JSON file
def load_api_keys():
    """
    Load API keys from .api-keys.json file.
    Returns dict with valid keys, super_user key, and rate limit config.
    """
    if not os.path.exists(API_KEYS_FILE):
        logger.warning(f"API keys file not found: {API_KEYS_FILE}")
        logger.warning("Running without authentication - NOT RECOMMENDED FOR PRODUCTION")
        return {
            'keys': set(),
            'super_user': None,
            'rate_limit': {'requests_per_minute': 60, 'requests_per_hour': 1000}
        }
    
    try:
        with open(API_KEYS_FILE, 'r') as f:
            data = json.load(f)
            
        # Extract super user key
        super_user_key = None
        if 'super_user' in data and data['super_user'].get('key'):
            super_user_key = data['super_user']['key']
            logger.info(f"Loaded super user: {data['super_user'].get('name', 'Unknown')}")
        
        # Extract only active API keys
        valid_keys = set()
        for key_info in data.get('api_keys', []):
            if key_info.get('active', False):
                valid_keys.add(key_info['key'])
                logger.info(f"Loaded active API key: {key_info.get('name', 'Unknown')}")
        
        rate_limit = data.get('rate_limit', {
            'requests_per_minute': 60,
            'requests_per_hour': 1000
        })
        
        logger.info(f"Loaded {len(valid_keys)} active API keys")
        return {
            'keys': valid_keys,
            'super_user': super_user_key,
            'rate_limit': rate_limit
        }
        
    except Exception as e:
        logger.error(f"Error loading API keys: {str(e)}")
        return {
            'keys': set(),
            'super_user': None,
            'rate_limit': {'requests_per_minute': 60, 'requests_per_hour': 1000}
        }

# Load version info at startup
VERSION_INFO = load_version_info()

# Load API keys at startup
API_KEYS_CONFIG = load_api_keys()
VALID_API_KEYS = API_KEYS_CONFIG['keys']
SUPER_USER_KEY = API_KEYS_CONFIG['super_user']
RATE_LIMIT_CONFIG = API_KEYS_CONFIG['rate_limit']

def check_rate_limit(api_key):
    """
    Check if API key has exceeded rate limits.
    Returns (allowed: bool, message: str)
    """
    now = datetime.now()
    
    # Clean up old entries (older than 1 hour)
    rate_limit_storage[api_key] = [
        timestamp for timestamp in rate_limit_storage[api_key]
        if now - timestamp < timedelta(hours=1)
    ]
    
    requests = rate_limit_storage[api_key]
    
    # Check per-minute limit
    minute_ago = now - timedelta(minutes=1)
    requests_last_minute = sum(1 for ts in requests if ts > minute_ago)
    
    if requests_last_minute >= RATE_LIMIT_CONFIG['requests_per_minute']:
        return False, f"Rate limit exceeded: {RATE_LIMIT_CONFIG['requests_per_minute']} requests per minute"
    
    # Check per-hour limit
    requests_last_hour = len(requests)
    if requests_last_hour >= RATE_LIMIT_CONFIG['requests_per_hour']:
        return False, f"Rate limit exceeded: {RATE_LIMIT_CONFIG['requests_per_hour']} requests per hour"
    
    # Add current request
    rate_limit_storage[api_key].append(now)
    return True, "OK"

def require_api_key(f):
    """
    Decorator to require API key authentication with rate limiting.
    API key should be sent in the X-API-Key header.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if authentication is configured
        if not VALID_API_KEYS:
            logger.warning("No API keys configured - running without authentication")
            logger.warning("⚠️  SECURITY WARNING: Please configure .api-keys.json file")
            return f(*args, **kwargs)
        
        # Get API key from request header
        request_api_key = request.headers.get('X-API-Key')
        
        if not request_api_key:
            logger.warning(f"API request missing X-API-Key header from {request.remote_addr}")
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please provide X-API-Key header'
            }), 401
        
        # Validate API key
        if request_api_key not in VALID_API_KEYS:
            logger.warning(f"Invalid API key attempted from {request.remote_addr}: {request_api_key[:10]}...")
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 403
        
        # Check rate limiting
        allowed, message = check_rate_limit(request_api_key)
        if not allowed:
            logger.warning(f"Rate limit exceeded for key: {request_api_key[:10]}... from {request.remote_addr}")
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': message
            }), 429
        
        logger.info(f"Authenticated request from {request.remote_addr}")
        return f(*args, **kwargs)
    return decorated_function

def require_super_user(f):
    """
    Decorator to require super user authentication.
    Super user key should be sent in the X-Super-User-Key header.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if super user is configured
        if not SUPER_USER_KEY:
            logger.error("Super user not configured")
            return jsonify({
                'error': 'Admin access not configured',
                'message': 'Super user key not set in .api-keys.json'
            }), 500
        
        # Get super user key from request header
        request_super_key = request.headers.get('X-Super-User-Key')
        
        if not request_super_key:
            logger.warning(f"Admin request missing X-Super-User-Key header from {request.remote_addr}")
            return jsonify({
                'error': 'Admin authentication required',
                'message': 'Please provide X-Super-User-Key header'
            }), 401
        
        # Validate super user key
        if request_super_key != SUPER_USER_KEY:
            logger.warning(f"Invalid super user key attempted from {request.remote_addr}")
            return jsonify({
                'error': 'Invalid super user key',
                'message': 'The provided super user key is not valid'
            }), 403
        
        logger.info(f"Super user authenticated from {request.remote_addr}")
        return f(*args, **kwargs)
    return decorated_function

def html_to_pdf_playwright(html_content, options=None):
    """
    Convert HTML to PDF using Playwright with headless Chromium.
    This renders HTML exactly like a real browser, handling all errors gracefully.
    
    Args:
        html_content: Raw HTML string
        options: PDF generation options dict
        
    Returns:
        bytes: PDF content
    """
    if options is None:
        options = {}
    
    temp_file = None
    
    try:
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            
            # Set viewport size
            viewport_width = options.get('viewport_width', 1920)
            viewport_height = options.get('viewport_height', 1080)
            
            # Create context and page with viewport
            context = browser.new_context(
                viewport={'width': viewport_width, 'height': viewport_height}
            )
            page = context.new_page()
            
            # Write HTML to temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            temp_file.write(html_content)
            temp_file.close()
            
            # Load the HTML file
            file_url = f"file:///{temp_file.name.replace(chr(92), '/')}"
            page.goto(file_url, wait_until='networkidle')
            
            # Build PDF options
            pdf_options = {
                'print_background': True,
                'prefer_css_page_size': False
            }
            
            # Set page size
            page_size = options.get('page_size', 'A4')
            if page_size and page_size.lower() != 'auto':
                pdf_options['format'] = page_size
            
            # Set margins
            margin = options.get('margin', '0')
            try:
                # Extract numeric value and convert to pixels
                margin_val = margin.replace('px', '').replace('cm', '').replace('mm', '')
                margin_val = float(margin_val) if margin_val else 0
                margin_str = f"{margin_val}px"
            except:
                margin_str = '0px'
            
            pdf_options['margin'] = {
                'top': margin_str,
                'right': margin_str,
                'bottom': margin_str,
                'left': margin_str
            }
            
            # Set custom dimensions if provided
            width = options.get('width')
            height = options.get('height')
            if width:
                pdf_options['width'] = width
            if height:
                pdf_options['height'] = height
            
            # Generate PDF
            pdf_bytes = page.pdf(**pdf_options)
            
            # Close browser
            browser.close()
            
            return pdf_bytes
            
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass

@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint with API documentation.
    """
    return jsonify({
        'service': VERSION_INFO.get('name', 'HTML to PDF Converter API'),
        'version': VERSION_INFO.get('version', __version__),
        'updated_at': VERSION_INFO.get('updated_at', __updated_at__),
        'endpoints': {
            '/': 'GET - API documentation',
            '/convert': 'POST - Convert HTML to PDF',
            '/health': 'GET - Health check',
            '/version': 'GET - API version and update info'
        },
        'usage': {
            'endpoint': '/convert',
            'method': 'POST',
            'content-type': 'application/json',
            'body': {
                'html': 'HTML content as string (required)',
                'css': 'Optional CSS styles as string (will be injected)',
                'filename': 'Optional output filename (default: document.pdf)',
                'base_url': 'Optional base URL for resolving relative URLs',
                'page_size': 'Optional: "A4" (default), "Letter", "Legal", "A3", etc. or "auto"',
                'width': 'Optional: Custom width (e.g., "1200px", "21cm")',
                'height': 'Optional: Custom height (e.g., "800px", "29.7cm")',
                'margin': 'Optional: Page margins (default: "0")',
                'viewport_width': 'Optional: Browser viewport width in pixels (default: 1920)',
                'viewport_height': 'Optional: Browser viewport height in pixels (default: 1080)'
            },
            'improvements': [
                '✅ Renders HTML exactly like Chrome browser',
                '✅ Handles broken HTML gracefully - no more syntax errors!',
                '✅ Automatically fixes malformed DOCTYPE, unclosed tags, etc.',
                '✅ Perfect for email templates with errors',
                '✅ Supports all CSS that works in browsers',
                '✅ Handles JavaScript-generated content',
                '✅ External resources load correctly'
            ],
            'example': {
                'description': 'Convert HTML with errors (works perfectly!)',
                'curl': 'curl -X POST https://your-api.com/convert -H "Content-Type: application/json" -H "X-API-Key: your-key" -d \'{"html": "<div style=\\"maxheight:100px\\">Broken HTML!</div>", "filename": "output.pdf"}\' --output output.pdf'
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
        'version': VERSION_INFO.get('version', __version__),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/version', methods=['GET'])
def version():
    """
    Version endpoint - Returns current API version and last update timestamp.
    Public endpoint - no authentication required.
    """
    return jsonify({
        'version': VERSION_INFO.get('version', __version__),
        'name': VERSION_INFO.get('name', 'HTML-to-PDF API'),
        'updated_at': VERSION_INFO.get('updated_at', __updated_at__),
        'changelog': VERSION_INFO.get('changelog', []),
        'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/convert', methods=['POST'])
@require_api_key
def convert_html_to_pdf():
    """
    Convert HTML to PDF using Puppeteer (headless Chrome).
    Renders HTML exactly like a browser, handling all syntax errors gracefully.
    
    Expects JSON payload with:
    - html: HTML content (required)
    - css: CSS styles (optional - will be injected into HTML)
    - filename: Output PDF filename (optional, default: document.pdf)
    - base_url: Base URL for resolving relative URLs (optional)
    - page_size: 'auto' for content-sized, or 'A4', 'Letter', 'Legal', etc. (default: 'A4')
    - width: Custom width (optional, e.g., '1200px', '21cm')
    - height: Custom height (optional, e.g., '800px', '29.7cm')
    - margin: Page margins (optional, default: '0')
    - viewport_width: Browser viewport width (optional, default: 1920)
    - viewport_height: Browser viewport height (optional, default: 1080)
    
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
        
        # Extract optional parameters
        css_content = data.get('css', '')
        filename = data.get('filename', 'document.pdf')
        base_url = data.get('base_url', None)
        page_size = data.get('page_size', 'A4')
        width = data.get('width', None)
        height = data.get('height', None)
        margin = data.get('margin', '0')
        viewport_width = data.get('viewport_width', 1920)
        viewport_height = data.get('viewport_height', 1080)
        
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        logger.info(f"Converting HTML to PDF with Puppeteer: {filename} (page_size={page_size})")
        
        # Inject CSS into HTML if provided
        if css_content:
            # Add style tag to HTML
            if '<head>' in html_content.lower():
                css_tag = f'<style>{css_content}</style>'
                html_content = html_content.replace('</head>', f'{css_tag}</head>', 1)
                html_content = html_content.replace('</HEAD>', f'{css_tag}</HEAD>', 1)
            else:
                # Add head section with CSS
                html_content = f'<!DOCTYPE html><html><head><style>{css_content}</style></head><body>{html_content}</body></html>'
        
        # Build Puppeteer options
        options = {
            'base_url': base_url,
            'page_size': page_size,
            'width': width,
            'height': height,
            'margin': margin,
            'viewport_width': viewport_width,
            'viewport_height': viewport_height
        }
        
        # Convert HTML to PDF using Playwright with headless Chromium
        pdf_bytes = html_to_pdf_playwright(html_content, options)
        
        pdf_buffer = io.BytesIO(pdf_bytes)
        pdf_buffer.seek(0)
        
        logger.info(f"PDF generated successfully: {filename} ({len(pdf_bytes)} bytes)")
        
        # Return PDF as downloadable file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error converting HTML to PDF: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Failed to convert HTML to PDF: {str(e)}',
            'type': type(e).__name__
        }), 500

# ============================================================================
# ADMIN ENDPOINTS - API Key Management (Super User Only)
# ============================================================================

@app.route('/admin/keys', methods=['GET'])
@require_super_user
def list_api_keys():
    """
    List all API keys (admin only).
    Requires X-Super-User-Key header.
    """
    try:
        with open(API_KEYS_FILE, 'r') as f:
            data = json.load(f)
        
        # Mask keys for security
        masked_keys = []
        for key_info in data.get('api_keys', []):
            masked_keys.append({
                'name': key_info['name'],
                'key_preview': key_info['key'][:8] + '...' + key_info['key'][-4:],
                'created': key_info.get('created', 'Unknown'),
                'active': key_info.get('active', False)
            })
        
        return jsonify({
            'success': True,
            'keys': masked_keys,
            'total': len(masked_keys),
            'rate_limit': data.get('rate_limit', {})
        })
        
    except Exception as e:
        logger.error(f"Error listing API keys: {str(e)}")
        return jsonify({'error': f'Failed to list keys: {str(e)}'}), 500

@app.route('/admin/keys', methods=['POST'])
@require_super_user
def create_api_key():
    """
    Create a new API key (admin only).
    Requires X-Super-User-Key header.
    
    Body:
    {
        "name": "Client Name",
        "active": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Key name is required'}), 400
        
        # Generate secure key
        import secrets
        new_key = secrets.token_urlsafe(32)
        
        # Load existing data
        with open(API_KEYS_FILE, 'r') as f:
            keys_data = json.load(f)
        
        # Add new key
        new_key_info = {
            'key': new_key,
            'name': data['name'],
            'created': datetime.now().strftime('%Y-%m-%d'),
            'active': data.get('active', True)
        }
        
        keys_data['api_keys'].append(new_key_info)
        
        # Save
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(keys_data, f, indent=2)
        
        # Reload keys in memory
        global VALID_API_KEYS, API_KEYS_CONFIG
        API_KEYS_CONFIG = load_api_keys()
        VALID_API_KEYS = API_KEYS_CONFIG['keys']
        
        logger.info(f"Created new API key: {data['name']}")
        
        return jsonify({
            'success': True,
            'message': 'API key created successfully',
            'key': new_key,
            'name': data['name'],
            'active': new_key_info['active'],
            'warning': 'Save this key securely. It will not be shown again in full.'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}")
        return jsonify({'error': f'Failed to create key: {str(e)}'}), 500

@app.route('/admin/keys/<key_prefix>', methods=['PATCH'])
@require_super_user
def update_api_key(key_prefix):
    """
    Update an API key (activate/deactivate or rename).
    Requires X-Super-User-Key header.
    
    Body:
    {
        "active": false,
        "name": "New Name (optional)"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        # Load existing data
        with open(API_KEYS_FILE, 'r') as f:
            keys_data = json.load(f)
        
        # Find and update key
        found = False
        for key_info in keys_data['api_keys']:
            if key_info['key'].startswith(key_prefix):
                if 'active' in data:
                    key_info['active'] = data['active']
                if 'name' in data:
                    key_info['name'] = data['name']
                found = True
                logger.info(f"Updated API key: {key_info['name']}")
                break
        
        if not found:
            return jsonify({'error': f'No key found with prefix: {key_prefix}'}), 404
        
        # Save
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(keys_data, f, indent=2)
        
        # Reload keys in memory
        global VALID_API_KEYS, API_KEYS_CONFIG
        API_KEYS_CONFIG = load_api_keys()
        VALID_API_KEYS = API_KEYS_CONFIG['keys']
        
        return jsonify({
            'success': True,
            'message': 'API key updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating API key: {str(e)}")
        return jsonify({'error': f'Failed to update key: {str(e)}'}), 500

@app.route('/admin/keys/<key_prefix>', methods=['DELETE'])
@require_super_user
def delete_api_key(key_prefix):
    """
    Delete an API key permanently (admin only).
    Requires X-Super-User-Key header.
    """
    try:
        # Load existing data
        with open(API_KEYS_FILE, 'r') as f:
            keys_data = json.load(f)
        
        # Find and remove key
        original_count = len(keys_data['api_keys'])
        keys_data['api_keys'] = [
            key_info for key_info in keys_data['api_keys']
            if not key_info['key'].startswith(key_prefix)
        ]
        
        if len(keys_data['api_keys']) == original_count:
            return jsonify({'error': f'No key found with prefix: {key_prefix}'}), 404
        
        # Save
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(keys_data, f, indent=2)
        
        # Reload keys in memory
        global VALID_API_KEYS, API_KEYS_CONFIG
        API_KEYS_CONFIG = load_api_keys()
        VALID_API_KEYS = API_KEYS_CONFIG['keys']
        
        logger.info(f"Deleted API key with prefix: {key_prefix}")
        
        return jsonify({
            'success': True,
            'message': 'API key deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting API key: {str(e)}")
        return jsonify({'error': f'Failed to delete key: {str(e)}'}), 500

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
