import json
import logging
import time
import random
from datetime import datetime
from modules.ping_services import PingServices  
from modules.proxy_rotation import ProxyRotationManager
from modules.advanced_indexing import AdvancedIndexingMethods
from config import Config

logger = logging.getLogger(__name__)

class ProfessionalIndexer:
    """
    Professional backlink indexing system with advanced rotation capabilities
    Replaces any need for Tor with legitimate proxy services and sophisticated rotation
    """
    
    def __init__(self, enable_proxy_rotation=False, rotation_interval=10):
        self.config = Config()
        self.enable_proxy_rotation = enable_proxy_rotation
        self.rotation_interval = rotation_interval
        self.request_count = 0
        
        # Initialize managers
        self.ping_services = PingServices()
        self.proxy_manager = ProxyRotationManager() if enable_proxy_rotation else None
        self.advanced_indexer = AdvancedIndexingMethods()
        
        # Track performance
        self.session_stats = {
            'total_requests': 0,
            'successful_pings': 0,
            'failed_pings': 0,
            'ip_rotations': 0,
            'start_time': datetime.now()
        }
    
    def setup_professional_rotation(self):
        """Initialize professional rotation system"""
        logger.info("Setting up professional indexing system...")
        
        if self.enable_proxy_rotation:
            if self.proxy_manager:
                stats = self.proxy_manager.get_rotation_stats()
                logger.info(f"Proxy rotation enabled: {stats['proxy_configured']}")
                logger.info(f"Available User-Agents: {stats['user_agents_available']}")
                return True
            else:
                logger.warning("Proxy rotation requested but not available")
                return False
        else:
            logger.info("Using standard rotation without proxies")
            return True
    
    def professional_ping_campaign(self, urls, campaign_name="Professional Campaign", 
                                 categories=None, include_advanced=True):
        """
        Execute professional ping campaign with rotation
        """
        campaign_results = {
            'campaign_name': campaign_name,
            'urls_count': len(urls),
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'proxy_rotation': self.enable_proxy_rotation,
                'rotation_interval': self.rotation_interval,
                'categories': categories or 'all',
                'advanced_methods': include_advanced
            },
            'results': {
                'traditional_pings': {},
                'advanced_methods': {},
                'rotation_stats': {}
            }
        }
        
        try:
            logger.info(f"Starting professional campaign: {campaign_name}")
            logger.info(f"Processing {len(urls)} URLs with rotation every {self.rotation_interval} requests")
            
            # Phase 1: Traditional ping services with rotation
            if self.enable_proxy_rotation and self.proxy_manager:
                campaign_results['results']['traditional_pings'] = self._execute_rotating_pings(
                    urls, categories=categories
                )
            else:
                campaign_results['results']['traditional_pings'] = self.ping_services.comprehensive_ping(
                    urls, campaign_id=campaign_name, categories=categories,
                    include_advanced=False  # We'll handle advanced separately
                )
            
            # Phase 2: Advanced indexing methods
            if include_advanced:
                logger.info("Executing advanced indexing methods...")
                advanced_results = self.advanced_indexer.comprehensive_advanced_indexing(
                    urls, campaign_id=campaign_name
                )
                
                # Enhanced distributed crawling with proxy support
                enhanced_crawling = self.advanced_indexer.simulate_distributed_crawling(
                    urls, crawl_count=min(20, len(urls)), 
                    use_proxy_rotation=self.enable_proxy_rotation
                )
                advanced_results['enhanced_crawling'] = enhanced_crawling
                
                campaign_results['results']['advanced_methods'] = advanced_results
            
            # Phase 3: Rotation statistics
            if self.proxy_manager:
                campaign_results['results']['rotation_stats'] = self.proxy_manager.get_rotation_stats()
            
            # Calculate success metrics
            self._calculate_campaign_metrics(campaign_results)
            
            logger.info(f"Professional campaign completed: {campaign_name}")
            return campaign_results
            
        except Exception as e:
            logger.error(f"Professional campaign failed: {str(e)}")
            campaign_results['error'] = str(e)
            return campaign_results
    
    def _execute_rotating_pings(self, urls, categories=None):
        """Execute ping services with professional rotation"""
        from modules.rss_generator import RSSGenerator
        from modules.sitemap_manager import SitemapManager
        
        rotating_results = {
            'rss_pings': {},
            'sitemap_pings': {},
            'service_summary': {
                'total_services_used': 0,
                'successful_pings': 0,
                'failed_pings': 0,
                'rotation_events': 0
            }
        }
        
        try:
            # Generate RSS feeds
            rss_gen = RSSGenerator()
            feeds = rss_gen.generate_multiple_feeds(urls, campaign_id="professional")
            
            for feed_type, feed_data in feeds.items():
                if feed_data:
                    # Use rotating ping services
                    rss_results = self._ping_with_rotation(
                        feed_data['url'], 'rss', categories=categories
                    )
                    rotating_results['rss_pings'][feed_type] = rss_results
            
            # Generate and ping sitemap with rotation
            sitemap_mgr = SitemapManager()
            sitemap_url = sitemap_mgr.create_sitemap(urls, campaign_id="professional")
            if sitemap_url:
                sitemap_results = self._ping_with_rotation(sitemap_url, 'sitemap')
                rotating_results['sitemap_pings'] = sitemap_results
            
            # Update summary statistics
            self._update_rotation_summary(rotating_results)
            
        except Exception as e:
            logger.error(f"Rotating pings failed: {str(e)}")
            rotating_results['error'] = str(e)
        
        return rotating_results
    
    def _ping_with_rotation(self, target_url, ping_type='rss', categories=None):
        """Ping services with automatic rotation"""
        results = {}
        
        if ping_type == 'rss':
            # Get RSS services
            services = []
            if categories:
                for category in categories:
                    if category in self.ping_services.rss_services:
                        services.extend([(svc, category) for svc in self.ping_services.rss_services[category]])
            else:
                # Use all categories
                for category, svc_list in self.ping_services.rss_services.items():
                    services.extend([(svc, category) for svc in svc_list])
            
            # Randomize service order
            random.shuffle(services)
            
            for service_url, category in services:
                # Check for rotation
                if self.request_count % self.rotation_interval == 0 and self.request_count > 0:
                    logger.info(f"Triggering rotation after {self.request_count} requests")
                    self.session_stats['ip_rotations'] += 1
                    time.sleep(random.uniform(2, 5))  # Pause for rotation effect
                
                # Make rotating request
                if self.proxy_manager:
                    result = self._make_professional_ping_request(service_url, target_url, category)
                else:
                    result = self._make_standard_ping_request(service_url, target_url, category)
                
                results[service_url] = result
                self.request_count += 1
                self.session_stats['total_requests'] += 1
                
                if result.get('success'):
                    self.session_stats['successful_pings'] += 1
                else:
                    self.session_stats['failed_pings'] += 1
                
                # Random delay between requests
                delay = random.uniform(0.5, 2.0)
                time.sleep(delay)
        
        elif ping_type == 'sitemap':
            # Handle sitemap pings with rotation
            if hasattr(self.ping_services, 'search_engines') and isinstance(self.ping_services.search_engines, dict):
                engines = list(self.ping_services.search_engines.items())
                random.shuffle(engines)
            else:
                engines = []
            
            for engine_name, base_url in engines:
                if self.request_count % self.rotation_interval == 0 and self.request_count > 0:
                    logger.info(f"Sitemap rotation after {self.request_count} requests")
                    self.session_stats['ip_rotations'] += 1
                    time.sleep(random.uniform(2, 4))
                
                ping_url = f"{base_url}{target_url}"
                
                if self.proxy_manager:
                    result = self.proxy_manager.make_rotating_request(ping_url, method='GET')
                else:
                    result = self._make_standard_sitemap_request(ping_url, engine_name)
                
                results[engine_name] = result
                self.request_count += 1
                self.session_stats['total_requests'] += 1
                
                time.sleep(random.uniform(1, 3))
        
        return results
    
    def _make_professional_ping_request(self, service_url, target_url, category):
        """Make professional ping request with rotation"""
        try:
            # Prepare ping data based on service type
            if "pingomatic" in service_url.lower():
                data = {
                    'title': 'Professional SEO Campaign',
                    'blogurl': 'https://professional-indexer.com',
                    'rssurl': target_url,
                    'chk_weblogscom': '1',
                    'chk_blogs': '1',
                    'chk_technorati': '1'
                }
            else:
                data = {
                    'name': 'Professional SEO Campaign',
                    'url': 'https://professional-indexer.com',
                    'changesURL': target_url
                }
            
            # Use proxy rotation manager
            result = self.proxy_manager.make_rotating_request(
                service_url, method='POST', data=data
            )
            
            if result['success']:
                return {
                    'success': True,
                    'status_code': result.get('status_code'),
                    'category': category,
                    'method': 'POST',
                    'proxy_used': True,
                    'headers_used': result.get('headers_used', {}),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error'),
                    'category': category,
                    'proxy_used': True,
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'category': category,
                'timestamp': datetime.now().isoformat()
            }
    
    def _make_standard_ping_request(self, service_url, target_url, category):
        """Make standard ping request without proxies"""
        try:
            import requests
            
            data = {
                'name': 'SEO Campaign',
                'url': 'https://indexer.com',
                'changesURL': target_url
            }
            
            headers = {
                'User-Agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                ]),
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(service_url, data=data, headers=headers, timeout=10)
            success = response.status_code in [200, 201, 202]
            
            return {
                'success': success,
                'status_code': response.status_code,
                'category': category,
                'method': 'POST',
                'proxy_used': False,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'category': category,
                'timestamp': datetime.now().isoformat()
            }
    
    def _make_standard_sitemap_request(self, ping_url, engine_name):
        """Make standard sitemap request"""
        try:
            import requests
            
            response = requests.get(ping_url, timeout=10)
            success = response.status_code in [200, 201, 202]
            
            return {
                'success': success,
                'status_code': response.status_code,
                'ping_url': ping_url,
                'proxy_used': False,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'ping_url': ping_url,
                'timestamp': datetime.now().isoformat()
            }
    
    def _update_rotation_summary(self, results):
        """Update summary statistics"""
        total_services = 0
        successful = 0
        failed = 0
        
        for result_group in ['rss_pings', 'sitemap_pings']:
            if result_group in results:
                for service_results in results[result_group].values():
                    if isinstance(service_results, dict):
                        for result in service_results.values():
                            total_services += 1
                            if result.get('success'):
                                successful += 1
                            else:
                                failed += 1
        
        results['service_summary'].update({
            'total_services_used': total_services,
            'successful_pings': successful,
            'failed_pings': failed,
            'rotation_events': self.session_stats['ip_rotations']
        })
    
    def _calculate_campaign_metrics(self, campaign_results):
        """Calculate comprehensive campaign metrics"""
        metrics = {
            'overall_success_rate': 0.0,
            'traditional_success_rate': 0.0,
            'advanced_success_rate': 0.0,
            'total_services_contacted': 0,
            'unique_methods_used': [],
            'session_duration': (datetime.now() - self.session_stats['start_time']).total_seconds(),
            'requests_per_minute': 0.0
        }
        
        # Calculate traditional ping success rate
        traditional = campaign_results['results'].get('traditional_pings', {})
        if traditional:
            summary = traditional.get('service_summary', {})
            total_traditional = summary.get('total_services_used', 0)
            successful_traditional = summary.get('successful_pings', 0)
            
            if total_traditional > 0:
                metrics['traditional_success_rate'] = (successful_traditional / total_traditional) * 100
                metrics['total_services_contacted'] += total_traditional
                metrics['unique_methods_used'].append('Traditional Pings')
        
        # Calculate advanced methods success
        advanced = campaign_results['results'].get('advanced_methods', {})
        if advanced:
            metrics['unique_methods_used'].extend(['JavaScript Heartbeat', 'Distributed Crawling', 'Podcast Feeds'])
            
            # Check crawling success
            crawling = advanced.get('enhanced_crawling', {})
            if crawling:
                total_crawls = crawling.get('total_crawls', 0)
                successful_crawls = crawling.get('successful_crawls', 0)
                if total_crawls > 0:
                    metrics['advanced_success_rate'] = (successful_crawls / total_crawls) * 100
        
        # Overall success rate
        total_ops = metrics['total_services_contacted'] + advanced.get('enhanced_crawling', {}).get('total_crawls', 0)
        total_success = (traditional.get('service_summary', {}).get('successful_pings', 0) + 
                        advanced.get('enhanced_crawling', {}).get('successful_crawls', 0))
        
        if total_ops > 0:
            metrics['overall_success_rate'] = (total_success / total_ops) * 100
        
        # Requests per minute
        if metrics['session_duration'] > 0:
            metrics['requests_per_minute'] = (self.session_stats['total_requests'] / metrics['session_duration']) * 60
        
        campaign_results['metrics'] = metrics
    
    def get_session_summary(self):
        """Get comprehensive session summary"""
        return {
            'session_stats': self.session_stats,
            'configuration': {
                'proxy_rotation_enabled': self.enable_proxy_rotation,
                'rotation_interval': self.rotation_interval,
                'proxy_configured': bool(self.proxy_manager and self.proxy_manager.get_rotation_stats().get('proxy_configured'))
            },
            'capabilities': {
                'total_rss_services': sum(len(services) for services in self.ping_services.rss_services.values()) if isinstance(self.ping_services.rss_services, dict) else 0,
                'total_search_engines': len(self.ping_services.search_engines),
                'advanced_methods': ['JavaScript Heartbeat', 'Distributed Crawling', 'Podcast Feeds'],
                'proxy_support': self.enable_proxy_rotation
            }
        }