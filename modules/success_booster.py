import requests
import json
import logging
import time
import random
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from modules.proxy_rotation import ProxyRotationManager
import concurrent.futures
import threading

logger = logging.getLogger(__name__)

class SuccessRateBooster:
    """
    Advanced success rate optimization system for ping services
    Implements multiple strategies to maximize indexing success
    """
    
    def __init__(self):
        self.verified_services = {}
        self.failed_services = set()
        self.success_cache = {}
        self.proxy_manager = ProxyRotationManager()
        self.lock = threading.Lock()
        
        # High-success modern services
        self.priority_services = {
            'google': [
                'https://www.google.com/ping?sitemap=',
                'https://www.google.com/webmasters/tools/ping?sitemap=',
                'https://feedburner.google.com/fb/a/ping'
            ],
            'bing': [
                'https://www.bing.com/ping?sitemap=',
                'https://www.bing.com/webmaster/ping.aspx?siteMap='
            ],
            'modern_aggregators': [
                'https://pingomatic.com/ping/',
                'https://feedpinger.net/',
                'https://www.feedsubmitter.com/ping.php',
                'https://www.pingler.com/ping/',
                'https://www.feed-ping.com/ping'
            ],
            'blog_networks': [
                'https://rpc.pingomatic.com/',
                'https://blogsearch.google.com/ping/RPC2',
                'https://ping.feedburner.com/',
                'https://pubsubhubbub.appspot.com/'
            ]
        }
        
        # Alternative endpoints for failed services
        self.service_alternatives = {
            'pingomatic.com': [
                'https://pingomatic.com/ping/',
                'https://rpc.pingomatic.com/',
                'https://www.pingomatic.com/ping/'
            ],
            'google.com': [
                'https://www.google.com/ping?sitemap=',
                'https://feedburner.google.com/fb/a/ping',
                'https://blogsearch.google.com/ping/RPC2'
            ],
            'feedburner': [
                'https://feedburner.google.com/fb/a/ping',
                'https://ping.feedburner.com/',
                'https://feeds.feedburner.com/fb/a/ping'
            ]
        }
    
    def verify_service_health(self, service_url, timeout=10):
        """
        Verify if a ping service is currently operational
        """
        try:
            # Try different approaches based on service type
            if 'google.com' in service_url:
                # For Google services, try a HEAD request first
                response = requests.head(service_url.replace('?sitemap=', ''), 
                                       timeout=timeout, allow_redirects=True)
                return response.status_code in [200, 301, 302, 405]
            
            elif 'pingomatic' in service_url:
                # For Pingomatic, try the main page
                base_url = '/'.join(service_url.split('/')[:3])
                response = requests.get(base_url, timeout=timeout)
                return response.status_code == 200 and 'ping' in response.text.lower()
            
            else:
                # For other services, try a basic connectivity check
                response = requests.head(service_url, timeout=timeout, allow_redirects=True)
                return response.status_code in [200, 301, 302, 405, 501]
                
        except Exception as e:
            logger.debug(f"Service health check failed for {service_url}: {str(e)}")
            return False
    
    def get_verified_services(self):
        """
        Get list of currently working ping services
        """
        verified = []
        
        # Check priority services first
        for category, services in self.priority_services.items():
            for service in services:
                if self.verify_service_health(service):
                    verified.append({
                        'url': service,
                        'category': category,
                        'priority': 'high',
                        'method': self._get_optimal_method(service)
                    })
                    logger.info(f"Verified high-priority service: {service}")
        
        return verified
    
    def _get_optimal_method(self, service_url):
        """
        Determine the optimal ping method for a service
        """
        if 'google.com' in service_url and 'sitemap=' in service_url:
            return 'GET'
        elif 'pingomatic' in service_url:
            return 'POST'
        elif 'feedburner' in service_url:
            return 'POST'
        elif 'bing.com' in service_url:
            return 'GET'
        else:
            return 'POST'
    
    def create_optimized_payload(self, service_url, target_url, title="SEO Campaign"):
        """
        Create optimized payload for different service types
        """
        parsed = urlparse(service_url)
        domain = parsed.netloc.lower()
        
        if 'google.com' in domain:
            if 'sitemap=' in service_url:
                return None  # URL parameter method
            else:
                return {
                    'name': title,
                    'url': 'https://professional-seo.com',
                    'changesURL': target_url
                }
        
        elif 'pingomatic' in domain:
            return {
                'title': title,
                'blogurl': 'https://professional-seo.com', 
                'rssurl': target_url,
                'chk_weblogscom': '1',
                'chk_blogs': '1',
                'chk_technorati': '1',
                'chk_feedburner': '1',
                'chk_syndic8': '1',
                'chk_newsgator': '1'
            }
        
        elif 'bing.com' in domain:
            return None  # URL parameter method
            
        elif 'feedburner' in domain:
            return {
                'name': title,
                'url': 'https://professional-seo.com',
                'changesURL': target_url
            }
            
        else:
            # Generic payload for other services
            return {
                'name': title,
                'url': 'https://professional-seo.com',
                'changesURL': target_url,
                'rssurl': target_url
            }
    
    def enhanced_ping_request(self, service_data, target_url, use_proxy=False):
        """
        Make an enhanced ping request with multiple fallback strategies
        """
        service_url = service_data['url']
        method = service_data['method']
        
        try:
            # Prepare request
            if method == 'GET' and ('sitemap=' in service_url or 'siteMap=' in service_url):
                # URL parameter method for sitemaps
                final_url = service_url + target_url
                payload = None
            else:
                final_url = service_url
                payload = self.create_optimized_payload(service_url, target_url)
            
            # Enhanced headers
            headers = {
                'User-Agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            if payload:
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
            
            # Make request with proxy rotation if enabled
            if use_proxy:
                if method == 'GET':
                    result = self.proxy_manager.make_rotating_request(final_url, method='GET')
                else:
                    result = self.proxy_manager.make_rotating_request(final_url, method='POST', data=payload)
                
                if result['success']:
                    response = result['response']
                    success = self._evaluate_response_success(response, service_url)
                    return {
                        'success': success,
                        'status_code': response.status_code,
                        'service_url': service_url,
                        'method': method,
                        'proxy_used': True,
                        'response_time': getattr(response, 'elapsed', None)
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('error', 'Proxy request failed'),
                        'service_url': service_url
                    }
            
            else:
                # Standard request
                session = requests.Session()
                session.headers.update(headers)
                
                if method == 'GET':
                    response = session.get(final_url, timeout=15, allow_redirects=True)
                else:
                    response = session.post(final_url, data=payload, timeout=15, allow_redirects=True)
                
                success = self._evaluate_response_success(response, service_url)
                
                return {
                    'success': success,
                    'status_code': response.status_code,
                    'service_url': service_url,
                    'method': method,
                    'proxy_used': False,
                    'response_time': response.elapsed,
                    'response_text': response.text[:200] if success else None
                }
                
        except Exception as e:
            logger.error(f"Enhanced ping failed for {service_url}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'service_url': service_url
            }
    
    def _evaluate_response_success(self, response, service_url):
        """
        Intelligently evaluate if a ping was successful
        """
        status_code = response.status_code
        response_text = response.text.lower() if hasattr(response, 'text') else ''
        
        # Google services
        if 'google.com' in service_url:
            if status_code in [200, 202]:
                return True
            elif status_code in [301, 302] and 'google' in response.headers.get('location', ''):
                return True
                
        # Pingomatic services  
        elif 'pingomatic' in service_url:
            if status_code == 200:
                success_indicators = ['success', 'ping', 'submitted', 'thank you', 'completed']
                return any(indicator in response_text for indicator in success_indicators)
                
        # Bing services
        elif 'bing.com' in service_url:
            return status_code in [200, 202]
            
        # FeedBurner services
        elif 'feedburner' in service_url or 'feeds.feedburner' in service_url:
            if status_code in [200, 202]:
                return 'error' not in response_text or 'success' in response_text
                
        # Generic evaluation
        else:
            if status_code in [200, 201, 202]:
                error_indicators = ['error', 'failed', 'invalid', 'not found', '404', '500']
                success_indicators = ['success', 'ok', 'submitted', 'received', 'ping']
                
                has_error = any(indicator in response_text for indicator in error_indicators)
                has_success = any(indicator in response_text for indicator in success_indicators)
                
                if has_success and not has_error:
                    return True
                elif not has_error and len(response_text) > 50:  # Assume success if no clear error
                    return True
        
        return False
    
    def parallel_ping_execution(self, target_urls, max_workers=5, use_proxy=False):
        """
        Execute pings in parallel for maximum efficiency
        """
        verified_services = self.get_verified_services()
        
        if not verified_services:
            logger.warning("No verified services available")
            return {'success': False, 'error': 'No working services found'}
        
        logger.info(f"Using {len(verified_services)} verified services for parallel execution")
        
        all_results = []
        
        def ping_service_for_url(service_data, url):
            try:
                # Add random delay to avoid overwhelming services
                time.sleep(random.uniform(0.5, 2.0))
                result = self.enhanced_ping_request(service_data, url, use_proxy=use_proxy)
                result['target_url'] = url
                return result
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'service_url': service_data['url'],
                    'target_url': url
                }
        
        # Execute pings in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for url in target_urls:
                for service_data in verified_services:
                    future = executor.submit(ping_service_for_url, service_data, url)
                    futures.append(future)
            
            # Collect results with timeout
            for future in concurrent.futures.as_completed(futures, timeout=300):
                try:
                    result = future.result(timeout=30)
                    all_results.append(result)
                except concurrent.futures.TimeoutError:
                    logger.warning("Ping request timed out")
                except Exception as e:
                    logger.error(f"Parallel ping execution error: {str(e)}")
        
        # Analyze results
        total_pings = len(all_results)
        successful_pings = sum(1 for r in all_results if r.get('success'))
        success_rate = (successful_pings / total_pings * 100) if total_pings > 0 else 0
        
        return {
            'success': True,
            'total_pings': total_pings,
            'successful_pings': successful_pings,
            'success_rate': success_rate,
            'verified_services_used': len(verified_services),
            'results': all_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def adaptive_retry_strategy(self, failed_services, target_url, max_retries=3):
        """
        Implement adaptive retry with alternative endpoints
        """
        retry_results = []
        
        for service_url in failed_services:
            domain = urlparse(service_url).netloc
            base_domain = '.'.join(domain.split('.')[-2:])  # Get base domain
            
            # Find alternative endpoints
            alternatives = []
            for key, alt_list in self.service_alternatives.items():
                if key in base_domain or base_domain in key:
                    alternatives.extend(alt_list)
            
            # Try alternatives
            for alt_url in alternatives[:max_retries]:
                if alt_url != service_url:  # Don't retry the same URL
                    logger.info(f"Retrying with alternative endpoint: {alt_url}")
                    
                    service_data = {
                        'url': alt_url,
                        'method': self._get_optimal_method(alt_url),
                        'category': 'retry'
                    }
                    
                    result = self.enhanced_ping_request(service_data, target_url, use_proxy=True)
                    retry_results.append(result)
                    
                    if result['success']:
                        logger.info(f"Retry successful with {alt_url}")
                        break
                    
                    time.sleep(random.uniform(2, 5))  # Wait between retries
        
        return retry_results
    
    def comprehensive_success_boost(self, target_urls, enable_proxy=False):
        """
        Comprehensive success rate boosting strategy
        """
        logger.info(f"Starting comprehensive success boost for {len(target_urls)} URLs")
        
        # Phase 1: Parallel ping execution with verified services
        phase1_results = self.parallel_ping_execution(target_urls, max_workers=5, use_proxy=enable_proxy)
        
        # Phase 2: Adaptive retry for failed services
        failed_services = [r['service_url'] for r in phase1_results.get('results', []) if not r.get('success')]
        
        retry_results = []
        if failed_services:
            logger.info(f"Phase 2: Retrying {len(set(failed_services))} failed services with alternatives")
            for url in target_urls:
                retry_batch = self.adaptive_retry_strategy(set(failed_services), url)
                retry_results.extend(retry_batch)
        
        # Phase 3: Additional modern service discovery
        phase3_results = self._discover_and_test_new_services(target_urls)
        
        # Combine all results
        all_results = phase1_results.get('results', []) + retry_results + phase3_results
        
        total_pings = len(all_results)
        successful_pings = sum(1 for r in all_results if r.get('success'))
        final_success_rate = (successful_pings / total_pings * 100) if total_pings > 0 else 0
        
        logger.info(f"Comprehensive boost completed: {final_success_rate:.1f}% success rate")
        
        return {
            'success': True,
            'total_pings': total_pings,
            'successful_pings': successful_pings,
            'success_rate': final_success_rate,
            'phase1_success_rate': phase1_results.get('success_rate', 0),
            'retry_attempts': len(retry_results),
            'new_services_tested': len(phase3_results),
            'all_results': all_results,
            'summary': {
                'verified_services': len(self.get_verified_services()),
                'proxy_enabled': enable_proxy,
                'urls_processed': len(target_urls),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _discover_and_test_new_services(self, target_urls):
        """
        Discover and test additional working ping services
        """
        # Additional modern services to test
        discovery_services = [
            'https://www.feedage.com/ping.php',
            'https://www.a2ping.com/ping.php',
            'https://www.blogpeople.net/servlet/submit',
            'https://www.moreover.com/ping',
            'https://api.my.yahoo.com/RPC2',
            'https://www.blogdigger.com/RPC2',
            'https://www.weblogues.com/RPC/',
            'https://blo.gs/ping.php',
            'https://www.blogshares.com/rpc.php',
            'https://www.snipsnap.org/RPC2'
        ]
        
        working_services = []
        test_results = []
        
        # Quick health check on discovery services
        for service_url in discovery_services:
            if self.verify_service_health(service_url, timeout=5):
                working_services.append({
                    'url': service_url,
                    'method': 'POST',
                    'category': 'discovered'
                })
        
        # Test working services with a sample URL
        if working_services and target_urls:
            sample_url = target_urls[0]  # Use first URL for testing
            
            for service_data in working_services[:5]:  # Test max 5 new services
                result = self.enhanced_ping_request(service_data, sample_url)
                if result['success']:
                    # If successful, ping all URLs with this service
                    for url in target_urls:
                        url_result = self.enhanced_ping_request(service_data, url)
                        test_results.append(url_result)
                        time.sleep(random.uniform(1, 3))
        
        return test_results