"""
Configuration for Tor Reverse Proxy
"""
import os

# Target website to proxy
TARGET_URL = "https://swisstargetprediction.ch"

# Check if running in Docker or if 'tor' hostname is resolvable
# Check if running in Docker or if 'tor' hostname is resolvable
import socket
import logging

def get_valid_tor_host():
    """Try to find a resolvable Tor host"""
    candidates = ['tor', 'tor-proxy', '127.0.0.1']
    
    # If we are effectively in Docker (heuristic), prioritize service names
    if os.path.exists('/.dockerenv'):
        # Just logging, not changing logic flow yet
        pass
        
    for host in candidates:
        try:
            socket.gethostbyname(host)
            return host
        except socket.error:
            continue
            
    return "127.0.0.1"  # Fallback

DEFAULT_TOR_HOST = get_valid_tor_host()

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
