"""
Tor Client Wrapper - Handles Tor SOCKS proxy and IP rotation
"""
import time
import logging
import requests
from stem import Signal
from stem.control import Controller

import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TorClient:
    """Tor client wrapper with IP rotation support"""
    
    def __init__(self):
        self.socks_host = config.TOR_SOCKS_HOST
        self.socks_port = config.TOR_SOCKS_PORT
        self.control_host = config.TOR_CONTROL_HOST
        self.control_port = config.TOR_CONTROL_PORT
        self.control_password = config.TOR_CONTROL_PASSWORD
        self.session = self._create_session()
        self._last_ip = None
    
    def _create_session(self) -> requests.Session:
        """Create a requests session configured to use Tor SOCKS proxy"""
        session = requests.Session()
        proxy_url = f"socks5h://{self.socks_host}:{self.socks_port}"
        session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        session.timeout = config.REQUEST_TIMEOUT
        return session
    
    def get_current_ip(self) -> str:
        """Get the current Tor exit node IP address"""
        try:
            response = self.session.get(
                "https://api.ipify.org?format=json",
                timeout=config.REQUEST_TIMEOUT
            )
            ip = response.json().get('ip', 'Unknown')
            self._last_ip = ip
            return ip
        except Exception as e:
            logger.error(f"Failed to get current IP: {e}")
            return "Unknown"
    
    def switch_ip(self) -> bool:
        """
        Switch to a new Tor circuit to get a new IP address.
        Returns True if successful, False otherwise.
        """
        try:
            with Controller.from_port(
                address=self.control_host,
                port=self.control_port
            ) as controller:
                controller.authenticate(password=self.control_password)
                controller.signal(Signal.NEWNYM)
                logger.info("Sent NEWNYM signal to Tor, waiting for new circuit...")
                
            # Wait for the new circuit to be established
            time.sleep(config.IP_SWITCH_DELAY)
            
            # Recreate session to ensure new circuit is used
            self.session = self._create_session()
            
            # Verify IP changed
            new_ip = self.get_current_ip()
            if self._last_ip and new_ip != self._last_ip:
                logger.info(f"IP switched from {self._last_ip} to {new_ip}")
            else:
                logger.info(f"Current IP: {new_ip}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch IP: {e}")
            return False
    
    def check_connection(self) -> bool:
        """Check if Tor connection is working"""
        try:
            response = self.session.get(
                "https://check.torproject.org/api/ip",
                timeout=config.REQUEST_TIMEOUT
            )
            data = response.json()
            is_tor = data.get('IsTor', False)
            if is_tor:
                logger.info(f"Connected to Tor network. Exit IP: {data.get('IP')}")
            else:
                logger.warning("Not connected through Tor network!")
            return is_tor
        except Exception as e:
            logger.error(f"Tor connection check failed: {e}")
            return False
    
    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make a request through Tor with automatic IP switching on errors"""
        kwargs.setdefault('timeout', config.REQUEST_TIMEOUT)
        
        last_response = None
        
        for attempt in range(config.MAX_RETRIES):
            try:
                logger.info(f"Attempt {attempt + 1}/{config.MAX_RETRIES}: {method} {url}")
                response = self.session.request(method, url, **kwargs)
                last_response = response
                
                if response.status_code in config.RETRY_STATUS_CODES:
                    logger.warning(
                        f"Got status {response.status_code} on attempt {attempt + 1}/{config.MAX_RETRIES}"
                    )
                    
                    # Don't switch IP on last attempt
                    if attempt < config.MAX_RETRIES - 1:
                        logger.info("Switching IP and retrying...")
                        self.switch_ip()
                    else:
                        logger.warning(f"Max retries reached, returning {response.status_code} response")
                    continue
                
                # Success - return the response
                logger.info(f"Request successful with status {response.status_code}")
                return response
                
            except requests.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt < config.MAX_RETRIES - 1:
                    logger.info("Switching IP due to connection error...")
                    self.switch_ip()
                else:
                    raise
        
        # Return the last response (which has an error status code)
        if last_response is not None:
            return last_response
        
        # This should not happen, but just in case
        raise requests.RequestException("All retry attempts failed")


# Global Tor client instance
tor_client = TorClient()
