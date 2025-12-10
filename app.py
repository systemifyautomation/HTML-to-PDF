"""
HTML to PDF Converter API
A Flask-based REST API for converting HTML content to PDF documents.
"""

__version__ = "1.2.0"
__updated_at__ = "2025-12-10T15:00:00Z"

from flask import Flask, request, send_file, jsonify
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import io
import os
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv
from collections import defaultdict
import re
from urllib.parse import urljoin, urlparse

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

def sanitize_and_enhance_html(html_content, base_url=None):
    """
    Sanitize and enhance HTML for browser-like PDF rendering.
    Preserves all browser rendering behaviors.
    
    Args:
        html_content: Raw HTML string
        base_url: Base URL for resolving relative URLs
    
    Returns:
        Enhanced HTML string
    """
    # Ensure HTML has proper structure
    if not re.search(r'<!DOCTYPE\s+html>', html_content, re.IGNORECASE):
        html_content = '<!DOCTYPE html>\n' + html_content
    
    # Ensure html tag exists
    if not re.search(r'<html[^>]*>', html_content, re.IGNORECASE):
        html_content = re.sub(r'<!DOCTYPE html>\s*', '<!DOCTYPE html>\n<html>\n', html_content, flags=re.IGNORECASE)
        html_content += '\n</html>'
    
    # Ensure head tag exists
    if not re.search(r'<head[^>]*>', html_content, re.IGNORECASE):
        html_content = re.sub(r'(<html[^>]*>)', r'\1\n<head></head>', html_content, flags=re.IGNORECASE)
    
    # Ensure body tag exists
    if not re.search(r'<body[^>]*>', html_content, re.IGNORECASE):
        # Find content between </head> and </html> or start of content
        html_content = re.sub(r'(</head>\s*)', r'\1<body>\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'(</html>)', r'</body>\n\1', html_content, flags=re.IGNORECASE)
    
    # Add charset if missing
    if not re.search(r'<meta[^>]*charset', html_content, re.IGNORECASE):
        html_content = re.sub(
            r'(<head[^>]*>)',
            r'\1\n    <meta charset="UTF-8">',
            html_content,
            flags=re.IGNORECASE
        )
    
    # Add viewport meta tag for responsive rendering
    if not re.search(r'<meta[^>]*viewport', html_content, re.IGNORECASE):
        html_content = re.sub(
            r'(<meta charset="UTF-8">)',
            r'\1\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            html_content,
            flags=re.IGNORECASE
        )
    
    # Add base tag if base_url is provided
    if base_url and not re.search(r'<base[^>]*href', html_content, re.IGNORECASE):
        html_content = re.sub(
            r'(<head[^>]*>)',
            f'\\1\n    <base href="{base_url}">',
            html_content,
            flags=re.IGNORECASE
        )
    
    return html_content

def get_default_pdf_css():
    """
    Get default CSS optimizations for PDF rendering that mimics browser display.
    
    Returns:
        CSS string with browser-like styles
    """
    return """
        /* Reset for consistent rendering */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* Browser-like defaults */
        html {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: 16px;
            line-height: 1.5;
            color: #000000;
            background: #ffffff;
        }
        
        body {
            margin: 8px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }
        
        /* Headings - match browser defaults */
        h1 { font-size: 2em; margin: 0.67em 0; font-weight: bold; }
        h2 { font-size: 1.5em; margin: 0.83em 0; font-weight: bold; }
        h3 { font-size: 1.17em; margin: 1em 0; font-weight: bold; }
        h4 { font-size: 1em; margin: 1.33em 0; font-weight: bold; }
        h5 { font-size: 0.83em; margin: 1.67em 0; font-weight: bold; }
        h6 { font-size: 0.67em; margin: 2.33em 0; font-weight: bold; }
        
        /* Paragraphs */
        p { margin: 1em 0; }
        
        /* Lists - browser defaults */
        ul, ol { 
            margin: 1em 0; 
            padding-left: 40px; 
        }
        
        ul { list-style-type: disc; }
        ol { list-style-type: decimal; }
        
        li { margin: 0.5em 0; }
        
        /* Links */
        a {
            color: #0000EE;
            text-decoration: underline;
        }
        
        a:visited {
            color: #551A8B;
        }
        
        /* Images */
        img {
            max-width: 100%;
            height: auto;
            display: inline-block;
            vertical-align: middle;
        }
        
        /* Tables - browser defaults */
        table {
            border-collapse: separate;
            border-spacing: 2px;
            border-color: gray;
        }
        
        th, td {
            padding: 1px;
            text-align: inherit;
        }
        
        th {
            font-weight: bold;
        }
        
        /* Forms */
        input, button, select, textarea {
            font-family: inherit;
            font-size: 100%;
            margin: 0;
        }
        
        button, input {
            overflow: visible;
        }
        
        /* Code blocks */
        code, pre {
            font-family: "Courier New", Courier, monospace;
            font-size: 0.875em;
        }
        
        pre {
            margin: 1em 0;
            padding: 10px;
            background: #f5f5f5;
            border: 1px solid #ccc;
            overflow: auto;
        }
        
        code {
            background: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        /* Blockquotes */
        blockquote {
            margin: 1em 40px;
            padding-left: 10px;
            border-left: 4px solid #ccc;
        }
        
        /* HR */
        hr {
            border: none;
            border-top: 1px solid #ccc;
            margin: 1em 0;
        }
        
        /* Text formatting */
        strong, b { font-weight: bold; }
        em, i { font-style: italic; }
        u { text-decoration: underline; }
        s, del { text-decoration: line-through; }
        mark { background-color: yellow; color: black; }
        small { font-size: 0.8em; }
        
        /* Prevent awkward breaks */
        h1, h2, h3, h4, h5, h6 {
            page-break-after: avoid;
            page-break-inside: avoid;
        }
        
        table, figure, img {
            page-break-inside: avoid;
        }
        
        /* Divs and sections */
        div, section, article, aside, nav, header, footer {
            display: block;
        }
    """

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
                'css': 'Optional CSS styles as string',
                'filename': 'Optional output filename (default: document.pdf)',
                'base_url': 'Optional base URL for resolving relative URLs (for images, stylesheets, etc.)',
                'page_size': 'Optional: "auto" for screenshot-like (default), or "A4", "Letter", "Legal", etc.',
                'width': 'Optional: Custom width when page_size is "auto" (e.g., "1200px", "21cm")',
                'margin': 'Optional: Page margins in CSS units like "2cm", "1in" (default: "0" for auto mode)',
                'optimize': 'Optional: PDF optimization flag (default: true)'
            },
            'modes': {
                'screenshot': 'Default: page_size="auto", margin="0" - PDF sized exactly to content',
                'fixed_width': 'page_size="auto", width="1200px" - Fixed width, auto height',
                'standard': 'page_size="A4", margin="2cm" - Traditional document format'
            },
            'improvements': [
                'Automatic HTML structure validation and correction',
                'Smart page break handling',
                'Image and font optimization',
                'External resource loading via base_url',
                'Better text rendering and typography',
                'Responsive image sizing'
            ]
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
    Convert HTML content to PDF.
    
    Expects JSON payload with:
    - html: HTML content (required)
    - css: CSS styles (optional)
    - filename: Output PDF filename (optional, default: document.pdf)
    - base_url: Base URL for resolving relative URLs (optional)
    - page_size: 'auto' for screenshot-like (default), or 'A4', 'Letter', 'Legal', etc.
    - width: Custom width when using auto sizing (optional, e.g., '1200px', '21cm')
    - margin: Page margins in CSS units (optional, default: '0' for auto mode, '2cm' for fixed)
    - optimize: Enable PDF optimization (optional, default: true)
    
    Modes:
    - Screenshot mode (default): page_size='auto', margin='0' - PDF sized to content
    - Fixed width mode: page_size='auto', width='1200px' - Fixed width, auto height
    - Standard document: page_size='A4', margin='2cm' - Traditional format
    
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
        page_size = data.get('page_size', 'auto')  # 'auto' for screenshot-like, or 'A4', 'Letter', etc.
        width = data.get('width', None)  # Custom width for auto-sizing
        margin = data.get('margin', '0')  # Default to no margin for screenshot mode
        optimize = data.get('optimize', True)
        
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        logger.info(f"Converting HTML to PDF: {filename} (page_size={page_size}, width={width}, optimize={optimize})")
        
        # Sanitize and enhance HTML
        html_content = sanitize_and_enhance_html(html_content, base_url)
        
        # Build CSS with PDF optimizations
        stylesheets = []
        font_config = FontConfiguration()
        
        # Add default PDF CSS
        default_css = get_default_pdf_css()
        
        # Add custom page size and margins
        if page_size.lower() == 'auto':
            # Auto-size to content - screenshot mode
            if width:
                # Fixed width, auto height
                page_css = f"""
                    @page {{
                        size: {width} auto;
                        margin: {margin};
                    }}
                    body {{
                        width: {width};
                    }}
                """
            else:
                # Completely auto-sized
                page_css = f"""
                    @page {{
                        margin: {margin};
                    }}
                """
        else:
            # Fixed page size (A4, Letter, etc.)
            page_css = f"""
                @page {{
                    size: {page_size};
                    margin: {margin};
                }}
            """
        
        # Combine all CSS
        combined_css = default_css + page_css
        if css_content:
            combined_css += "\n" + css_content
        
        stylesheets.append(CSS(string=combined_css, font_config=font_config))
        
        # Create PDF from HTML with optimizations
        pdf_buffer = io.BytesIO()
        
        html_obj = HTML(string=html_content, base_url=base_url, encoding='utf-8')
        html_obj.write_pdf(
            pdf_buffer,
            stylesheets=stylesheets,
            font_config=font_config,
            optimize_size=('fonts', 'images') if optimize else ()
        )
        
        # Reset buffer position to beginning
        pdf_buffer.seek(0)
        
        logger.info(f"PDF generated successfully: {filename} ({pdf_buffer.getbuffer().nbytes} bytes)")
        
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
