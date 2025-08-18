import json
import logging
from urllib.parse import urlparse
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class ServiceCleaner:
    """
    Clean up old/broken services and replace with modern working alternatives
    """
    
    def __init__(self):
        # Modern replacement services for old/broken ones
        self.modern_replacements = {
            # Replace HTTP with HTTPS versions
            'http://pingomatic.com/ping/': 'https://pingomatic.com/ping/',
            'http://rpc.pingomatic.com/': 'https://rpc.pingomatic.com/',
            
            # Replace broken services with working alternatives
            'http://rpc.technorati.com/rpc/ping': 'https://feedburner.google.com/fb/a/ping',
            'http://www.feedsubmitter.com/ping/': 'https://www.feedsubmitter.com/ping.php',
            'http://www.pingler.com/ping/': 'https://www.pingler.com/ping/',
            
            # Remove completely broken services (map to None)
            'http://www.blogpeople.net/ping/': None,
            'http://www.blogflux.com/ping/': None,
            'http://www.syndic8.com/ping': None,
            'http://xping.pubsub.com/ping/': None,
            'http://www.feedshark.brainbliss.com/ping/': None,
            'http://www.newsisfree.com/RPCCloud': None,
            'http://ping.blo.gs/': None,
            'http://rpc.weblogs.com/RPC2': None,
            'http://rcs.datashed.net/RPC2/': None,
            'http://www.weblogalot.com/ping/': None,
            'http://blo.gs/ping.php': None,
            'http://www.popdex.com/addsite': None,
            'http://www.blogdigger.com/RPC2': None,
            'http://www.blogstreet.com/xrbin/xmlrpc.cgi': None,
            'http://bulkpingtool.com/ping': None,
            'http://www.blogshares.com/rpc.php': None,
            'http://www.pingoat.com/goat/RPC2': None,
            'http://ping.feedvalidator.org/rpc': None,
            'http://rpc.icerocket.com:10080/': None,
            'http://www.pingmyblog.com': None,
            'http://api.moreover.com/ping?': None
        }
        
        # Modern services to add
        self.modern_additions = [
            'https://feedburner.google.com/fb/a/ping',
            'https://pubsubhubbub.appspot.com/publish',
            'https://www.google.com/ping?sitemap=',
            'https://www.bing.com/ping?sitemap=',
            'https://api.indexnow.org/indexnow'
        ]
    
    def clean_rss_services(self, services_file='ping_lists/rss_services.json'):
        """
        Clean and update RSS services list
        """
        try:
            with open(services_file, 'r') as f:
                services_data = json.load(f)
            
            cleaned_data = {}
            total_removed = 0
            total_updated = 0
            
            for category, services in services_data.items():
                cleaned_services = []
                
                for service_url in services:
                    if service_url in self.modern_replacements:
                        replacement = self.modern_replacements[service_url]
                        if replacement:
                            cleaned_services.append(replacement)
                            total_updated += 1
                            logger.info(f"Updated service: {service_url} -> {replacement}")
                        else:
                            total_removed += 1
                            logger.info(f"Removed broken service: {service_url}")
                    else:
                        # Keep existing service
                        cleaned_services.append(service_url)
                
                # Remove duplicates while preserving order
                seen = set()
                cleaned_data[category] = []
                for service in cleaned_services:
                    if service not in seen:
                        seen.add(service)
                        cleaned_data[category].append(service)
            
            # Add modern services to appropriate categories
            if 'google_services' not in cleaned_data:
                cleaned_data['google_services'] = []
            
            for modern_service in self.modern_additions:
                if 'google.com' in modern_service or 'feedburner' in modern_service:
                    if modern_service not in cleaned_data['google_services']:
                        cleaned_data['google_services'].append(modern_service)
                elif 'bing.com' in modern_service:
                    if 'search_engines' not in cleaned_data:
                        cleaned_data['search_engines'] = []
                    if modern_service not in cleaned_data['search_engines']:
                        cleaned_data['search_engines'].append(modern_service)
                else:
                    if modern_service not in cleaned_data.get('global_rss', []):
                        if 'global_rss' not in cleaned_data:
                            cleaned_data['global_rss'] = []
                        cleaned_data['global_rss'].append(modern_service)
            
            # Write cleaned services back
            with open(services_file, 'w') as f:
                json.dump(cleaned_data, f, indent=2)
            
            logger.info(f"Service cleanup completed: {total_updated} updated, {total_removed} removed")
            
            return {
                'success': True,
                'updated': total_updated,
                'removed': total_removed,
                'total_services': sum(len(services) for services in cleaned_data.values()),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cleaning services: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def verify_service_endpoints(self, services_file='ping_lists/rss_services.json', timeout=5):
        """
        Verify that service endpoints are still accessible
        """
        try:
            with open(services_file, 'r') as f:
                services_data = json.load(f)
            
            verification_results = {}
            working_services = {}
            broken_services = []
            
            for category, services in services_data.items():
                verification_results[category] = {}
                working_services[category] = []
                
                for service_url in services:
                    try:
                        # Try to access the service
                        parsed_url = urlparse(service_url)
                        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                        
                        if 'sitemap=' in service_url or '?' in service_url:
                            # For parameterized URLs, test the base endpoint
                            test_url = base_url
                        else:
                            test_url = service_url
                        
                        response = requests.head(test_url, timeout=timeout, allow_redirects=True)
                        
                        # Consider 200, 301, 302, 405 (Method Not Allowed) as working
                        is_working = response.status_code in [200, 301, 302, 405]
                        
                        verification_results[category][service_url] = {
                            'working': is_working,
                            'status_code': response.status_code,
                            'response_time': response.elapsed.total_seconds()
                        }
                        
                        if is_working:
                            working_services[category].append(service_url)
                        else:
                            broken_services.append(service_url)
                            
                    except Exception as e:
                        verification_results[category][service_url] = {
                            'working': False,
                            'error': str(e)
                        }
                        broken_services.append(service_url)
            
            # Calculate statistics
            total_services = sum(len(services) for services in services_data.values())
            total_working = sum(len(services) for services in working_services.values())
            success_rate = (total_working / total_services * 100) if total_services > 0 else 0
            
            return {
                'success': True,
                'total_services': total_services,
                'working_services': total_working,
                'broken_services': len(broken_services),
                'success_rate': success_rate,
                'verification_results': verification_results,
                'working_services_by_category': working_services,
                'broken_service_urls': broken_services,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error verifying services: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_optimized_service_list(self, min_success_rate=80):
        """
        Create a new optimized service list with only high-success services
        """
        # High-success modern services
        optimized_services = {
            'primary_search_engines': [
                'https://www.google.com/ping?sitemap=',
                'https://www.bing.com/ping?sitemap=',
                'https://webmaster.yandex.com/ping?sitemap='
            ],
            'google_services': [
                'https://feedburner.google.com/fb/a/ping',
                'https://blogsearch.google.com/ping/RPC2',
                'https://pubsubhubbub.appspot.com/publish'
            ],
            'verified_aggregators': [
                'https://pingomatic.com/ping/',
                'https://www.feedsubmitter.com/ping.php',
                'https://www.pingler.com/ping/'
            ],
            'modern_apis': [
                'https://api.indexnow.org/indexnow'
            ]
        }
        
        # Write optimized list
        optimized_file = 'ping_lists/optimized_services.json'
        try:
            with open(optimized_file, 'w') as f:
                json.dump(optimized_services, f, indent=2)
            
            total_services = sum(len(services) for services in optimized_services.values())
            
            return {
                'success': True,
                'optimized_file': optimized_file,
                'total_services': total_services,
                'categories': list(optimized_services.keys()),
                'expected_success_rate': min_success_rate,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating optimized service list: {str(e)}")
            return {'success': False, 'error': str(e)}