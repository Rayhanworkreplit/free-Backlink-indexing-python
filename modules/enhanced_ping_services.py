"""
Enhanced Ping Services Module
Handles the new ping services with improved categorization and performance
"""

import json
import requests
import logging
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Set, Tuple, Optional

logger = logging.getLogger(__name__)

class EnhancedPingServices:
    def __init__(self):
        self.load_all_services()
        self.retry_attempts = 3
        self.backoff_factor = 2
        self.timeout_settings = {
            'modern_ping_services': 10,
            'seo_tools': 15,
            'bulk_ping': 20,
            'developer_tools': 10,
            'blog_ping': 10,
            'hosting_tools': 15,
            'google_tools': 20,
            'indexing_tools': 20,
            'directory_submission': 25,
            'traditional_ping': 10,
            'google_services': 15,
            'global_rss': 10,
            'regional_services': 10,
            'validation_services': 20
        }
        
    def load_all_services(self):
        """Load all ping services from JSON files"""
        self.all_services = {}
        
        try:
            with open('ping_lists/rss_services.json', 'r') as f:
                data = json.load(f)
                self.all_services.update(data)
        except Exception as e:
            logger.error(f"Failed to load RSS services: {e}")
            
        logger.info(f"Loaded {sum(len(services) for services in self.all_services.values())} total ping services")
        
    def get_service_categories(self) -> List[str]:
        """Get all available service categories"""
        return list(self.all_services.keys())
        
    def get_services_by_category(self, categories: Optional[List[str]] = None) -> List[str]:
        """Get services from specific categories"""
        if categories is None:
            categories = self.get_service_categories()
            
        services = []
        for category in categories:
            if category in self.all_services:
                services.extend(self.all_services[category])
                
        return services
        
    def get_service_stats(self) -> Dict[str, int]:
        """Get statistics about available services"""
        stats = {}
        for category, services in self.all_services.items():
            stats[category] = len(services)
        stats['total'] = sum(stats.values())
        return stats
        
    def ping_urls_enhanced(self, urls: List[str], selected_categories: Optional[List[str]] = None) -> Dict:
        """Enhanced ping function with better performance and reporting"""
        if not urls:
            return {'success': False, 'message': 'No URLs provided'}
            
        # Get services from selected categories
        services = self.get_services_by_category(selected_categories)
        
        if not services:
            return {'success': False, 'message': 'No services available for selected categories'}
            
        # Randomize service order for better distribution
        random.shuffle(services)
        
        results = {
            'campaign_start': datetime.now().isoformat(),
            'urls_processed': len(urls),
            'services_used': len(services),
            'categories': selected_categories if selected_categories is not None else self.get_service_categories(),
            'results': [],
            'summary': {
                'total_pings': 0,
                'successful_pings': 0,
                'failed_pings': 0,
                'service_success_rate': {},
                'category_performance': {}
            }
        }
        
        # Process pings with thread pool for better performance
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for url in urls:
                for service in services:
                    category = self._get_service_category(service)
                    future = executor.submit(self._ping_single_service, url, service, category)
                    futures.append(future)
                    
            # Process results as they complete
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    if result:
                        results['results'].append(result)
                        results['summary']['total_pings'] += 1
                        
                        if result['success']:
                            results['summary']['successful_pings'] += 1
                        else:
                            results['summary']['failed_pings'] += 1
                            
                        # Track per-service success rates
                        service = result['service']
                        if service not in results['summary']['service_success_rate']:
                            results['summary']['service_success_rate'][service] = {'attempts': 0, 'successes': 0}
                        
                        results['summary']['service_success_rate'][service]['attempts'] += 1
                        if result['success']:
                            results['summary']['service_success_rate'][service]['successes'] += 1
                            
                except Exception as e:
                    logger.error(f"Future result error: {e}")
                    
        # Calculate final statistics
        if results['summary']['total_pings'] > 0:
            success_rate = (results['summary']['successful_pings'] / results['summary']['total_pings']) * 100
            results['summary']['overall_success_rate'] = round(success_rate, 2)
        else:
            results['summary']['overall_success_rate'] = 0
            
        # Calculate per-service success percentages
        for service, stats in results['summary']['service_success_rate'].items():
            if stats['attempts'] > 0:
                stats['success_percentage'] = round((stats['successes'] / stats['attempts']) * 100, 2)
            else:
                stats['success_percentage'] = 0
                
        results['campaign_end'] = datetime.now().isoformat()
        logger.info(f"Ping campaign completed: {results['summary']['successful_pings']}/{results['summary']['total_pings']} successful")
        
        return results
        
    def _get_service_category(self, service_url: str) -> str:
        """Determine which category a service belongs to"""
        for category, services in self.all_services.items():
            if service_url in services:
                return category
        return 'unknown'
        
    def _ping_single_service(self, url: str, service: str, category: str) -> Dict:
        """Ping a single service with retry logic"""
        timeout = self.timeout_settings.get(category, 10)
        
        for attempt in range(self.retry_attempts):
            try:
                # Add random delay to prevent overwhelming services
                time.sleep(random.uniform(0.1, 0.5))
                
                # Prepare the ping request
                data = self._prepare_ping_data(url, service)
                headers = self._get_ping_headers(service)
                
                response = requests.post(
                    service,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                    verify=False  # Some services have SSL issues
                )
                
                success = response.status_code == 200
                
                return {
                    'url': url,
                    'service': service,
                    'category': category,
                    'success': success,
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'attempt': attempt + 1,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                if attempt == self.retry_attempts - 1:  # Last attempt
                    return {
                        'url': url,
                        'service': service,
                        'category': category,
                        'success': False,
                        'error': str(e),
                        'attempt': attempt + 1,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    # Wait before retry with exponential backoff
                    wait_time = self.backoff_factor ** attempt + random.uniform(0, 1)
                    time.sleep(wait_time)
                    
        return {
            'url': url,
            'service': service,
            'category': category,
            'success': False,
            'error': 'Max retries exceeded',
            'timestamp': datetime.now().isoformat()
        }
        
    def _prepare_ping_data(self, url: str, service: str) -> Dict:
        """Prepare ping data based on service requirements"""
        # Basic ping data structure
        data = {
            'url': url,
            'name': f'Ping for {url}',
            'rssurl': url,
            'blogurl': url,
            'website': url
        }
        
        # Service-specific data formatting
        if 'google' in service.lower():
            data['sitemap'] = url
            
        if 'rss' in service.lower() or 'feed' in service.lower():
            data['feedurl'] = url
            
        return data
        
    def _get_ping_headers(self, service: str) -> Dict:
        """Get appropriate headers for the ping service"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Service-specific headers
        if any(keyword in service.lower() for keyword in ['api', 'json']):
            headers['Content-Type'] = 'application/json'
        else:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            
        return headers
        
    def get_recommended_categories(self, campaign_type: str = 'general') -> List[str]:
        """Get recommended service categories based on campaign type"""
        recommendations = {
            'general': ['google_services', 'modern_ping_services', 'seo_tools', 'global_rss'],
            'seo_focused': ['seo_tools', 'google_tools', 'indexing_tools', 'modern_ping_services'],
            'bulk_indexing': ['bulk_ping', 'modern_ping_services', 'google_services', 'directory_submission'],
            'blog_ping': ['blog_ping', 'global_rss', 'traditional_ping', 'regional_services'],
            'comprehensive': list(self.all_services.keys())
        }
        
        return recommendations.get(campaign_type, recommendations['general'])
    
    def _get_service_category(self, service: str) -> str:
        """Get the category of a specific service"""
        for category, services in self.all_services.items():
            if service in services:
                return category
        return 'unknown'
    
    def _ping_single_service(self, url: str, service: str, category: str) -> Dict:
        """Ping a single service and return detailed result"""
        timeout = self.timeout_settings.get(category, 10)
        
        for attempt in range(self.retry_attempts):
            try:
                # Prepare the ping request
                data = self._prepare_ping_data(url, service)
                headers = self._get_ping_headers(service)
                
                start_time = time.time()
                response = requests.post(
                    service,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                    verify=False  # Some services have SSL issues
                )
                response_time = time.time() - start_time
                
                success = response.status_code == 200
                
                return {
                    'url': url,
                    'service': service,
                    'category': category,
                    'success': success,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'attempt': attempt + 1,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                if attempt == self.retry_attempts - 1:  # Last attempt
                    return {
                        'url': url,
                        'service': service,
                        'category': category,
                        'success': False,
                        'error': str(e),
                        'response_time': 0,
                        'attempt': attempt + 1,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    # Wait before retry with exponential backoff
                    wait_time = self.backoff_factor ** attempt + random.uniform(0, 1)
                    time.sleep(wait_time)
                    
        return {
            'url': url,
            'service': service,
            'category': category,
            'success': False,
            'error': 'Max retries exceeded',
            'response_time': 0,
            'timestamp': datetime.now().isoformat()
        }