import requests
import random
import time
import logging
import os
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class ProxyRotationManager:
    """
    Professional proxy rotation for SEO indexing campaigns
    Uses legitimate proxy services and User-Agent rotation
    """
    
    def __init__(self):
        self.config = Config()
        self.current_proxy_index = 0
        self.request_count = 0
        self.session_start = datetime.now()
        
        # Professional User-Agent rotation (expanded list)
        self.user_agents = [
            # Desktop Chrome (Windows)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Desktop Chrome (Mac)
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Desktop Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0',
            
            # Mobile Chrome
            'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            
            # Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # Accept-Language variations
        self.accept_languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.9',
            'en-CA,en;q=0.8,fr;q=0.6',
            'en-AU,en;q=0.9',
            'en-US,en;q=0.8,es;q=0.6',
            'en-US,en;q=0.9,de;q=0.8'
        ]
        
        # Professional proxy services (users would need to configure)
        self.proxy_providers = {
            'instructions': {
                'brightdata': 'Configure with BrightData residential proxies',
                'smartproxy': 'Use SmartProxy rotating residential IPs',
                'proxy_cheap': 'Set up Proxy-Cheap datacenter proxies',
                'note': 'Users should configure legitimate proxy services in environment variables'
            },
            'example_config': {
                'PROXY_HTTP': 'http://username:password@proxy-server:port',
                'PROXY_HTTPS': 'https://username:password@proxy-server:port'
            }
        }
    
    def get_rotating_headers(self):
        """Generate rotating headers to simulate different browsers"""
        user_agent = random.choice(self.user_agents)
        accept_language = random.choice(self.accept_languages)
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': accept_language,
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Randomly add some optional headers
        if random.random() < 0.7:
            headers['Sec-Ch-Ua'] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
            headers['Sec-Ch-Ua-Mobile'] = '?0' if 'Mobile' not in user_agent else '?1'
            headers['Sec-Ch-Ua-Platform'] = random.choice(['"Windows"', '"macOS"', '"Linux"'])
        
        return headers
    
    def create_session_with_rotation(self):
        """Create a requests session with rotation capabilities"""
        session = requests.Session()
        
        # Set rotating headers
        headers = self.get_rotating_headers()
        session.headers.update(headers)
        
        # Configure proxy if available (user must provide legitimate proxy service)
        proxy_http = os.environ.get('PROXY_HTTP')
        proxy_https = os.environ.get('PROXY_HTTPS')
        
        if proxy_http and proxy_https:
            session.proxies = {
                'http': proxy_http,
                'https': proxy_https
            }
            logger.info("Session configured with proxy rotation")
        else:
            logger.info("Session configured with User-Agent rotation only")
        
        return session
    
    def make_rotating_request(self, url, method='GET', **kwargs):
        """Make HTTP request with automatic rotation"""
        self.request_count += 1
        
        # Create new session periodically for better rotation
        if self.request_count % random.randint(5, 15) == 0:
            session = self.create_session_with_rotation()
        else:
            session = self.create_session_with_rotation()
        
        try:
            # Add random delay to simulate human behavior
            delay = random.uniform(1.0, 3.0)
            time.sleep(delay)
            
            # Make request
            if method.upper() == 'GET':
                response = session.get(url, timeout=10, **kwargs)
            elif method.upper() == 'POST':
                response = session.post(url, timeout=10, **kwargs)
            elif method.upper() == 'HEAD':
                response = session.head(url, timeout=5, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            logger.info(f"Request {self.request_count}: {method} {url} -> {response.status_code}")
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response': response,
                'headers_used': dict(session.headers),
                'request_count': self.request_count
            }
            
        except Exception as e:
            logger.error(f"Rotating request failed for {url}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'url': url,
                'request_count': self.request_count
            }
        finally:
            session.close()
    
    def bulk_rotate_requests(self, urls, method='HEAD'):
        """Perform bulk requests with rotation for multiple URLs"""
        results = []
        
        # Randomize URL order
        randomized_urls = random.sample(urls, len(urls))
        
        for i, url in enumerate(randomized_urls):
            logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
            
            result = self.make_rotating_request(url, method=method)
            result['url'] = url
            result['sequence'] = i + 1
            results.append(result)
            
            # Progressive delay increase to be respectful
            if i < len(urls) - 1:  # Don't delay after last request
                base_delay = 2.0 + (i * 0.1)  # Gradually increase delay
                jitter = random.uniform(-0.5, 0.5)
                delay = max(1.0, base_delay + jitter)
                time.sleep(delay)
        
        return results
    
    def get_rotation_stats(self):
        """Get statistics about current rotation session"""
        return {
            'total_requests': self.request_count,
            'session_duration': (datetime.now() - self.session_start).total_seconds(),
            'average_requests_per_minute': self.request_count / max(1, (datetime.now() - self.session_start).total_seconds() / 60),
            'user_agents_available': len(self.user_agents),
            'languages_available': len(self.accept_languages),
            'proxy_configured': bool(os.environ.get('PROXY_HTTP'))
        }

# Integration with existing ping services
def enhance_existing_ping_services():
    """Instructions for integrating rotation with existing services"""
    return {
        'integration_note': 'To integrate with existing ping services, replace direct requests calls with ProxyRotationManager.make_rotating_request()',
        'example_usage': '''
# In ping_services.py, replace:
response = requests.post(service_url, data=data, timeout=timeout)

# With:
rotation_manager = ProxyRotationManager()
result = rotation_manager.make_rotating_request(service_url, method='POST', data=data)
response = result.get('response') if result['success'] else None
        ''',
        'benefits': [
            'Distributed request patterns reduce rate limiting',
            'User-Agent rotation simulates diverse traffic sources',
            'Optional proxy support for advanced users',
            'Respectful rate limiting with progressive delays',
            'Professional header rotation for authenticity'
        ]
    }