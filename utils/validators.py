import re
import urllib.parse
import logging

logger = logging.getLogger(__name__)

class URLValidator:
    def __init__(self):
        # Comprehensive URL regex pattern
        self.url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        # Common suspicious domains/patterns to exclude
        self.suspicious_patterns = [
            r'\.onion$',  # Tor domains
            r'localhost',  # Localhost
            r'127\.0\.0\.1',  # Loopback
            r'192\.168\.',  # Private network
            r'10\.',  # Private network
            r'172\.1[6-9]\.',  # Private network
            r'172\.2[0-9]\.',  # Private network
            r'172\.3[0-1]\.',  # Private network
        ]
    
    def is_valid_url(self, url):
        """Validate if URL is properly formatted and safe"""
        try:
            if not url or not isinstance(url, str):
                return False
            
            url = url.strip()
            
            # Check basic format
            if not self.url_pattern.match(url):
                return False
            
            # Parse URL to validate components
            parsed = urllib.parse.urlparse(url)
            
            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check for suspicious patterns
            for pattern in self.suspicious_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    logger.warning(f"Suspicious URL pattern detected: {url}")
                    return False
            
            # Additional length check
            if len(url) > 2048:  # URLs longer than 2048 chars are problematic
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"URL validation error for {url}: {str(e)}")
            return False
    
    def clean_url(self, url):
        """Clean and normalize URL"""
        try:
            url = url.strip()
            
            # Remove common prefixes that users might add
            prefixes_to_remove = ['www.', 'http://www.', 'https://www.']
            for prefix in prefixes_to_remove:
                if url.lower().startswith(prefix) and not url.lower().startswith('http'):
                    url = url[len(prefix):]
            
            # Add https:// if no scheme
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Parse and reconstruct to normalize
            parsed = urllib.parse.urlparse(url)
            
            # Normalize scheme to lowercase
            scheme = parsed.scheme.lower()
            
            # Normalize domain to lowercase
            netloc = parsed.netloc.lower()
            
            # Remove default ports
            if ':80' in netloc and scheme == 'http':
                netloc = netloc.replace(':80', '')
            elif ':443' in netloc and scheme == 'https':
                netloc = netloc.replace(':443', '')
            
            # Reconstruct URL
            clean_url = urllib.parse.urlunparse((
                scheme,
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            
            return clean_url
            
        except Exception as e:
            logger.error(f"URL cleaning error for {url}: {str(e)}")
            return url
    
    def extract_domain(self, url):
        """Extract domain from URL"""
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.lower()
        except:
            return None
    
    def is_same_domain(self, url1, url2):
        """Check if two URLs are from the same domain"""
        try:
            domain1 = self.extract_domain(url1)
            domain2 = self.extract_domain(url2)
            return domain1 == domain2 and domain1 is not None
        except:
            return False
    
    def validate_bulk_urls(self, urls):
        """Validate a list of URLs and return valid/invalid lists"""
        valid_urls = []
        invalid_urls = []
        
        for url in urls:
            if self.is_valid_url(url):
                clean_url = self.clean_url(url)
                valid_urls.append(clean_url)
            else:
                invalid_urls.append(url)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_valid_urls = []
        for url in valid_urls:
            if url not in seen:
                seen.add(url)
                unique_valid_urls.append(url)
        
        return unique_valid_urls, invalid_urls
