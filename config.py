"""
Configuration for Tor Reverse Proxy
"""
import os

# Check if running in Docker or if 'tor' hostname is resolvable
import socket
def is_tor_resolvable():
    try:
        socket.gethostbyname('tor')
        return True
    except socket.error:
        return False

# Determine default based on environment
if os.path.exists('/.dockerenv') or is_tor_resolvable():
    DEFAULT_TOR_HOST = "tor"
else:
    DEFAULT_TOR_HOST = "127.0.0.1"

# Tor SOCKS proxy settings
TOR_SOCKS_HOST = os.getenv("TOR_SOCKS_HOST", DEFAULT_TOR_HOST)
TOR_SOCKS_PORT = int(os.getenv("TOR_SOCKS_PORT", 9050))

# Tor control port settings (for IP switching)
TOR_CONTROL_HOST = os.getenv("TOR_CONTROL_HOST", DEFAULT_TOR_HOST)
TOR_CONTROL_PORT = int(os.getenv("TOR_CONTROL_PORT", 9051))
TOR_CONTROL_PASSWORD = os.getenv("TOR_CONTROL_PASSWORD", "your_password_here")

# Proxy server settings
PROXY_HOST = os.getenv("PROXY_HOST", "0.0.0.0")
PROXY_PORT = int(os.getenv("PROXY_PORT", 5000))

# Authentication settings
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "true").lower() == "true"
AUTH_API_KEY = os.getenv("AUTH_API_KEY", "changeme123")  # Change this!

# Retry configuration
RETRY_STATUS_CODES = [403, 404, 429]  # Status codes that trigger IP switch
MAX_RETRIES = 3  # Maximum retry attempts per request
IP_SWITCH_DELAY = 5  # Seconds to wait after switching IP

# Request timeout
REQUEST_TIMEOUT = 30  # seconds

# Headers to skip when proxying (hop-by-hop headers)
SKIP_HEADERS = {
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade', 'host',
    'content-length', 'content-encoding'
}
