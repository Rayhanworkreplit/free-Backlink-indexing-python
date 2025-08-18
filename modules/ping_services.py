import json
import requests
import logging
import time
import threading
import random
from datetime import datetime
from config import Config
from modules.webhook_manager import WebhookManager

logger = logging.getLogger(__name__)

class PingServices:
    def __init__(self):
        self.config = Config()
        self.webhook_manager = WebhookManager()
        self.load_ping_services()
        self.retry_attempts = 3
        self.backoff_factor = 2
    
    def load_ping_services(self):
        """Load ping services from JSON files with new categorized structure"""
        try:
            with open('ping_lists/rss_services.json', 'r') as f:
                rss_data = json.load(f)
                # Load all categories including the new ones
                self.rss_services = {
                    'google_services': rss_data.get('google_services', []),
                    'global_rss': rss_data.get('global_rss', []),
                    'regional_services': rss_data.get('regional_services', []),
                    'validation_services': rss_data.get('validation_services', []),
                    'modern_ping_services': rss_data.get('modern_ping_services', []),
                    'seo_tools': rss_data.get('seo_tools', []),
                    'bulk_ping': rss_data.get('bulk_ping', []),
                    'developer_tools': rss_data.get('developer_tools', []),
                    'blog_ping': rss_data.get('blog_ping', []),
                    'hosting_tools': rss_data.get('hosting_tools', []),
                    'google_tools': rss_data.get('google_tools', []),
                    'indexing_tools': rss_data.get('indexing_tools', []),
                    'directory_submission': rss_data.get('directory_submission', []),
                    'traditional_ping': rss_data.get('traditional_ping', [])
                }
        except Exception as e:
            logger.error(f"Failed to load RSS services: {e}")
            self.rss_services = self._get_default_rss_services()
            
        try:
            with open('ping_lists/search_engines.json', 'r') as f:
                engine_data = json.load(f)
                self.search_engines = {
                    **engine_data.get('primary_engines', {}),
                    **engine_data.get('additional_engines', {})
                }
        except Exception as e:
            logger.error(f"Failed to load search engines: {e}")
            self.search_engines = self._get_default_search_engines()
            
        try:
            with open('ping_lists/directories.json', 'r') as f:
                dir_data = json.load(f)
                # Flatten directory categories
                self.directories = []
                self.directories.extend(dir_data.get('free_directories', []))
                self.directories.extend(dir_data.get('web_directories', []))
        except Exception as e:
            logger.error(f"Failed to load directories: {e}")
            self.directories = self._get_default_directories()
    
    def _get_default_rss_services(self):
        """Default RSS ping services"""
        return [
            "http://pingomatic.com/ping/",
            "http://www.feedsubmitter.com/ping/",
            "http://www.pingler.com/ping/",
            "http://www.blogpeople.net/ping/",
            "http://rpc.technorati.com/rpc/ping",
            "http://www.blogflux.com/ping/",
            "http://www.syndic8.com/ping",
            "http://xping.pubsub.com/ping/",
            "http://www.feedshark.brainbliss.com/ping/",
            "http://www.newsisfree.com/RPCCloud",
            "http://ping.blo.gs/",
            "http://rpc.weblogs.com/RPC2",
            "http://rcs.datashed.net/RPC2/",
            "http://www.weblogalot.com/ping/",
            "http://blo.gs/ping.php",
            "http://www.popdex.com/addsite",
            "http://www.blogdigger.com/RPC2",
            "http://www.blogstreet.com/xrbin/xmlrpc.cgi",
            "http://bulkpingtool.com/ping",
            "http://www.blogshares.com/rpc.php",
            "https://feedburner.google.com/fb/a/ping",
            "https://blogsearch.google.com/ping",
            "https://pubsubhubbub.appspot.com/publish"
        ]
    
    def _get_default_search_engines(self):
        """Default search engine ping services"""
        return {
            "google": "https://www.google.com/ping?sitemap=",
            "bing": "https://www.bing.com/webmaster/ping.aspx?siteMap=",
            "yandex": "https://webmaster.yandex.com/ping?sitemap="
        }
    
    def _get_default_directories(self):
        """Default directory submission services"""
        return [
            "https://www.dmoz-odp.org/public/suggest",
            "https://www.jayde.com/add_url.html",
            "https://www.exorank.com/addurl.php",
            "https://www.freewebsubmission.com/submit-url/"
        ]
    
    def ping_rss_services(self, rss_url, blog_name="SEO Feed", blog_url="http://localhost:5000", categories=None):
        """Ping RSS services with RSS feed URL using categorized approach"""
        results = {}
        
        # If no categories specified, use all
        if categories is None:
            categories = ['google_services', 'global_rss', 'regional_services', 'validation_services']
        
        # Collect all services from specified categories
        all_services = []
        for category in categories:
            if isinstance(self.rss_services, dict) and category in self.rss_services:
                services_in_category = self.rss_services[category]
                if isinstance(services_in_category, list):
                    category_services = [(service, category) for service in services_in_category]
                    all_services.extend(category_services)
        
        # Randomize ping order as recommended
        random.shuffle(all_services)
        
        for service_url, category in all_services:
            success = self._ping_rss_service_with_retry(service_url, rss_url, blog_name, blog_url, category)
            results[service_url] = success
            
            # Throttle requests with random delays
            delay = random.uniform(0.3, 0.8)
            time.sleep(delay)
        
        return results
    
    def _ping_rss_service_with_retry(self, service_url, rss_url, blog_name, blog_url, category):
        """Ping single RSS service with retry logic and backoff"""
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Pinging RSS service: {service_url} (attempt {attempt + 1})")
                
                # Enhanced parameter handling based on service type
                data = self._get_rss_ping_data(service_url, rss_url, blog_name, blog_url, category)
                
                # Try POST first, fallback to GET if needed
                method = 'POST'
                if any(keyword in service_url.lower() for keyword in ['validator', 'semanticsitemaps']):
                    method = 'GET'
                    service_url = f"{service_url}{rss_url}" if not service_url.endswith('=') else f"{service_url}{rss_url}"
                
                if method == 'POST':
                    response = requests.post(
                        service_url, 
                        data=data, 
                        timeout=self.config.RSS_PING_TIMEOUT,
                        headers={
                            'User-Agent': 'Free Ping Indexer Pro/1.0',
                            'Content-Type': 'application/x-www-form-urlencoded'
                        }
                    )
                else:
                    response = requests.get(
                        service_url,
                        timeout=self.config.RSS_PING_TIMEOUT,
                        headers={'User-Agent': 'Free Ping Indexer Pro/1.0'}
                    )
                
                success = response.status_code in [200, 201, 202]
                result = {
                    'success': success,
                    'status_code': response.status_code,
                    'response_text': response.text[:200] if success else response.text[:100],
                    'timestamp': datetime.now().isoformat(),
                    'category': category,
                    'method': method,
                    'attempt': attempt + 1
                }
                
                logger.info(f"RSS ping result for {service_url}: {success}")
                return result
                
            except Exception as e:
                logger.error(f"RSS ping failed for {service_url} (attempt {attempt + 1}): {str(e)}")
                
                if attempt < self.retry_attempts - 1:
                    # Exponential backoff
                    backoff_time = (self.backoff_factor ** attempt) + random.uniform(0.1, 0.5)
                    time.sleep(backoff_time)
                else:
                    return {
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat(),
                        'category': category,
                        'total_attempts': self.retry_attempts
                    }
    
    def _get_rss_ping_data(self, service_url, rss_url, blog_name, blog_url, category):
        """Get appropriate ping data based on service type"""
        # Google services specific parameters
        if category == 'google_services':
            if 'feedburner' in service_url:
                return {
                    'name': blog_name,
                    'url': blog_url,
                    'changesURL': rss_url
                }
            elif 'pubsubhubbub' in service_url:
                return {
                    'hub.mode': 'publish',
                    'hub.url': rss_url
                }
            elif 'blogsearch' in service_url:
                return {
                    'name': blog_name,
                    'url': blog_url,
                    'changesURL': rss_url
                }
        
        # Pingomatic specific parameters
        if "pingomatic" in service_url.lower():
            return {
                'title': blog_name,
                'blogurl': blog_url,
                'rssurl': rss_url,
                'chk_weblogscom': '1',
                'chk_blogs': '1',
                'chk_technorati': '1',
                'chk_feedburner': '1',
                'chk_syndic8': '1',
                'chk_newsgator': '1',
                'chk_myyahoo': '1',
                'chk_pubsubcom': '1',
                'chk_blogdigger': '1',
                'chk_weblogalot': '1',
                'chk_feedshark': '1',
                'chk_newsisfree': '1',
                'chk_feedster': '1',
                'chk_icerocket': '1'
            }
        
        # Standard parameters for most services
        return {
            'name': blog_name,
            'url': blog_url,
            'changesURL': rss_url
        }
    
    def ping_search_engines(self, sitemap_url):
        """Ping search engines with sitemap URL using enhanced retry logic"""
        results = {}
        
        # Randomize engine order
        engines = list(self.search_engines.items())
        random.shuffle(engines)
        
        for engine_name, base_url in engines:
            result = self._ping_search_engine_with_retry(engine_name, base_url, sitemap_url)
            results[engine_name] = result
            
            # Throttle requests with random delays
            delay = random.uniform(1.0, 2.0)
            time.sleep(delay)
        
        return results
    
    def _ping_search_engine_with_retry(self, engine_name, base_url, sitemap_url):
        """Ping single search engine with retry logic"""
        for attempt in range(self.retry_attempts):
            try:
                ping_url = f"{base_url}{sitemap_url}"
                logger.info(f"Pinging {engine_name}: {ping_url} (attempt {attempt + 1})")
                
                # Special handling for different engines
                headers = {'User-Agent': 'Free Ping Indexer Pro/1.0'}
                timeout = self.config.SITEMAP_PING_TIMEOUT
                
                if 'yahoo' in engine_name.lower() and 'appid=' in base_url:
                    # Yahoo requires an app ID, use as GET parameter
                    ping_url = f"{base_url}{sitemap_url}"
                
                response = requests.get(ping_url, timeout=timeout, headers=headers)
                
                success = response.status_code in [200, 201, 202]
                result = {
                    'success': success,
                    'status_code': response.status_code,
                    'ping_url': ping_url,
                    'timestamp': datetime.now().isoformat(),
                    'attempt': attempt + 1,
                    'response_text': response.text[:200] if success else response.text[:100]
                }
                
                logger.info(f"Search engine ping result for {engine_name}: {success}")
                return result
                
            except Exception as e:
                logger.error(f"Search engine ping failed for {engine_name} (attempt {attempt + 1}): {str(e)}")
                
                if attempt < self.retry_attempts - 1:
                    # Exponential backoff
                    backoff_time = (self.backoff_factor ** attempt) + random.uniform(0.5, 1.0)
                    time.sleep(backoff_time)
                else:
                    return {
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat(),
                        'total_attempts': self.retry_attempts
                    }
    
    def submit_to_directories(self, url):
        """Submit URL to free directories"""
        results = {}
        
        for directory_url in self.directories:
            try:
                logger.info(f"Submitting to directory: {directory_url}")
                
                # Most directories require form submission
                data = {
                    'url': url,
                    'title': f"Quality Content from {url}",
                    'description': f"Valuable content and resources from {url}"
                }
                
                response = requests.post(
                    directory_url,
                    data=data,
                    timeout=self.config.RSS_PING_TIMEOUT,
                    headers={'User-Agent': 'Free Ping Indexer Pro/1.0'}
                )
                
                success = response.status_code in [200, 201, 202]
                results[directory_url] = {
                    'success': success,
                    'status_code': response.status_code,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"Directory submission result for {directory_url}: {success}")
                
            except Exception as e:
                logger.error(f"Directory submission failed for {directory_url}: {str(e)}")
                results[directory_url] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            
            time.sleep(2)  # Longer delay for directory submissions
        
        return results
    
    def comprehensive_ping(self, urls, campaign_id=None, categories=None, include_archives=True, include_directories=True, include_advanced=False):
        """Execute comprehensive ping strategy for URLs with flexible campaign control"""
        from modules.rss_generator import RSSGenerator
        from modules.sitemap_manager import SitemapManager
        from modules.archive_tools import ArchiveTools
        from modules.advanced_indexing import AdvancedIndexingMethods
        
        results = {
            'campaign_id': campaign_id,
            'urls_count': len(urls),
            'timestamp': datetime.now().isoformat(),
            'rss_pings': {},
            'sitemap_pings': {},
            'archive_saves': {},
            'directory_submissions': {},
            'advanced_methods': {},
            'service_summary': {
                'total_rss_services': 0,
                'total_search_engines': 0,
                'successful_pings': 0,
                'failed_pings': 0,
                'advanced_methods_used': 0
            }
        }
        
        try:
            # Generate RSS feeds and ping with specified categories
            rss_gen = RSSGenerator()
            feeds = rss_gen.generate_multiple_feeds(urls, campaign_id)
            
            for feed_type, feed_data in feeds.items():
                if feed_data:
                    rss_results = self.ping_rss_services(feed_data['url'], categories=categories)
                    results['rss_pings'][feed_type] = rss_results
                    
                    # Update summary stats
                    for service_result in rss_results.values():
                        results['service_summary']['total_rss_services'] += 1
                        if service_result.get('success', False):
                            results['service_summary']['successful_pings'] += 1
                        else:
                            results['service_summary']['failed_pings'] += 1
            
            # Generate sitemap and ping search engines
            sitemap_mgr = SitemapManager()
            sitemap_url = sitemap_mgr.create_sitemap(urls, campaign_id)
            if sitemap_url:
                sitemap_results = self.ping_search_engines(sitemap_url)
                results['sitemap_pings'] = sitemap_results
                
                # Update summary stats
                for engine_result in sitemap_results.values():
                    results['service_summary']['total_search_engines'] += 1
                    if engine_result.get('success', False):
                        results['service_summary']['successful_pings'] += 1
                    else:
                        results['service_summary']['failed_pings'] += 1
            
            # Archive and directory submissions (optional)
            if include_archives or include_directories:
                archive_tools = ArchiveTools() if include_archives else None
                
                for url in urls:
                    if include_archives and archive_tools:
                        # Archive.org save
                        archive_result = archive_tools.trigger_archive_save(url)
                        results['archive_saves'][url] = archive_result
                    
                    if include_directories:
                        # Directory submissions
                        directory_results = self.submit_to_directories(url)
                        results['directory_submissions'][url] = directory_results
                    
                    # Rate limiting between URLs
                    time.sleep(random.uniform(0.5, 1.5))
            
            # Advanced indexing methods (optional)
            if include_advanced:
                logger.info("Executing advanced indexing methods...")
                advanced_indexer = AdvancedIndexingMethods()
                advanced_results = advanced_indexer.comprehensive_advanced_indexing(urls, campaign_id)
                results['advanced_methods'] = advanced_results
                results['service_summary']['advanced_methods_used'] = 3  # heartbeat, crawling, podcast
            
        except Exception as e:
            logger.error(f"Comprehensive ping failed: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def get_service_categories(self):
        """Get available service categories for flexible campaign control"""
        return {
            'rss_categories': list(self.rss_services.keys()) if isinstance(self.rss_services, dict) else [],
            'search_engines': list(self.search_engines.keys()),
            'directory_count': len(self.directories),
            'total_rss_services': sum(len(services) for services in self.rss_services.values()) if isinstance(self.rss_services, dict) else 0
        }
