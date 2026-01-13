"""
Reverse Proxy Server - Flask application that proxies requests through Tor
"""
import logging
from urllib.parse import urljoin
from flask import Flask, request, Response, jsonify

import config
from tor_client import tor_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def filter_headers(headers, skip_set):
    """Filter out hop-by-hop headers"""
    return {
        key: value for key, value in headers.items()
        if key.lower() not in skip_set
    }


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    tor_connected = tor_client.check_connection()
    return jsonify({
        'status': 'healthy' if tor_connected else 'degraded',
        'tor_connected': tor_connected
    })


@app.route('/api/current-ip', methods=['GET'])
def get_current_ip():
    """Get the current Tor exit IP"""
    ip = tor_client.get_current_ip()
    return jsonify({'ip': ip})


@app.route('/api/switch-ip', methods=['POST'])
def switch_ip():
    """Manually trigger IP switch"""
    old_ip = tor_client.get_current_ip()
    success = tor_client.switch_ip()
    new_ip = tor_client.get_current_ip()
    return jsonify({
        'success': success,
        'old_ip': old_ip,
        'new_ip': new_ip,
        'changed': old_ip != new_ip
    })


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def proxy(path):
    """
    Main proxy endpoint - forwards all requests to the target site through Tor
    """
    # Build the target URL
    target_url = urljoin(config.TARGET_URL + '/', path)
    if request.query_string:
        target_url += '?' + request.query_string.decode('utf-8')
    
    logger.info(f"Proxying {request.method} {target_url}")
    
    # Prepare headers
    headers = filter_headers(dict(request.headers), config.SKIP_HEADERS)
    headers['Host'] = 'swisstargetprediction.ch'
    
    # Prepare request kwargs
    kwargs = {
        'headers': headers,
        'allow_redirects': False,
    }
    
    # Add body for methods that support it
    if request.method in ['POST', 'PUT', 'PATCH']:
        if request.is_json:
            kwargs['json'] = request.get_json()
        elif request.form:
            kwargs['data'] = request.form.to_dict()
        elif request.files:
            # Handle file uploads
            files = {}
            for key, file in request.files.items():
                files[key] = (file.filename, file.stream, file.content_type)
            kwargs['files'] = files
            if request.form:
                kwargs['data'] = request.form.to_dict()
        else:
            kwargs['data'] = request.get_data()
    
    try:
        # Make the request through Tor
        resp = tor_client.request(request.method, target_url, **kwargs)
        
        # Build response
        response_headers = filter_headers(dict(resp.headers), config.SKIP_HEADERS)
        
        return Response(
            resp.content,
            status=resp.status_code,
            headers=response_headers
        )
        
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to proxy request'
        }), 502


if __name__ == '__main__':
    logger.info(f"Starting proxy server on {config.PROXY_HOST}:{config.PROXY_PORT}")
    logger.info(f"Target URL: {config.TARGET_URL}")
    logger.info(f"Tor SOCKS: {config.TOR_SOCKS_HOST}:{config.TOR_SOCKS_PORT}")
    
    # Check Tor connection on startup
    if tor_client.check_connection():
        logger.info(f"Current exit IP: {tor_client.get_current_ip()}")
    else:
        logger.warning("Tor connection not available - proxy may not work correctly")
    
    app.run(
        host=config.PROXY_HOST,
        port=config.PROXY_PORT,
        debug=False
    )
