import json
import requests
import logging
import time
import threading
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class PingServices:
    def __init__(self):
        self.config = Config()
        self.load_ping_services()
    
    def load_ping_services(self):
        """Load ping services from JSON files"""
        try:
            with open('ping_lists/rss_services.json', 'r') as f:
                self.rss_services = json.load(f)
        except:
            self.rss_services = self._get_default_rss_services()
            
        try:
            with open('ping_lists/search_engines.json', 'r') as f:
                self.search_engines = json.load(f)
        except:
            self.search_engines = self._get_default_search_engines()
            
        try:
            with open('ping_lists/directories.json', 'r') as f:
                self.directories = json.load(f)
        except:
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
    
    def ping_rss_services(self, rss_url, blog_name="SEO Feed", blog_url="http://localhost:5000"):
        """Ping RSS services with RSS feed URL"""
        results = {}
        
        for service_url in self.rss_services:
            try:
                logger.info(f"Pinging RSS service: {service_url}")
                
                # Different services expect different parameters
                if "pingomatic" in service_url:
                    data = {
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
                else:
                    # Standard parameters for most services
                    data = {
                        'name': blog_name,
                        'url': blog_url,
                        'changesURL': rss_url
                    }
                
                response = requests.post(
                    service_url, 
                    data=data, 
                    timeout=self.config.RSS_PING_TIMEOUT,
                    headers={
                        'User-Agent': 'Free Ping Indexer Pro/1.0',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                )
                
                success = response.status_code in [200, 201, 202]
                results[service_url] = {
                    'success': success,
                    'status_code': response.status_code,
                    'response_text': response.text[:200] if success else None,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"RSS ping result for {service_url}: {success}")
                
            except Exception as e:
                logger.error(f"RSS ping failed for {service_url}: {str(e)}")
                results[service_url] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            
            # Small delay between pings to be respectful
            time.sleep(0.5)
        
        return results
    
    def ping_search_engines(self, sitemap_url):
        """Ping search engines with sitemap URL"""
        results = {}
        
        for engine_name, base_url in self.search_engines.items():
            try:
                ping_url = f"{base_url}{sitemap_url}"
                logger.info(f"Pinging {engine_name}: {ping_url}")
                
                response = requests.get(
                    ping_url,
                    timeout=self.config.SITEMAP_PING_TIMEOUT,
                    headers={'User-Agent': 'Free Ping Indexer Pro/1.0'}
                )
                
                success = response.status_code in [200, 201, 202]
                results[engine_name] = {
                    'success': success,
                    'status_code': response.status_code,
                    'ping_url': ping_url,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"Search engine ping result for {engine_name}: {success}")
                
            except Exception as e:
                logger.error(f"Search engine ping failed for {engine_name}: {str(e)}")
                results[engine_name] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            
            time.sleep(1)  # Longer delay for search engines
        
        return results
    
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
    
    def comprehensive_ping(self, urls, campaign_id=None):
        """Execute comprehensive ping strategy for URLs"""
        from modules.rss_generator import RSSGenerator
        from modules.sitemap_manager import SitemapManager
        from modules.archive_tools import ArchiveTools
        
        results = {
            'campaign_id': campaign_id,
            'urls_count': len(urls),
            'timestamp': datetime.now().isoformat(),
            'rss_pings': {},
            'sitemap_pings': {},
            'archive_saves': {},
            'directory_submissions': {}
        }
        
        try:
            # Generate RSS feeds and ping
            rss_gen = RSSGenerator()
            feeds = rss_gen.generate_multiple_feeds(urls, campaign_id)
            
            for feed_type, feed_data in feeds.items():
                if feed_data:
                    rss_results = self.ping_rss_services(feed_data['url'])
                    results['rss_pings'][feed_type] = rss_results
            
            # Generate sitemap and ping search engines
            sitemap_mgr = SitemapManager()
            sitemap_url = sitemap_mgr.create_sitemap(urls, campaign_id)
            if sitemap_url:
                sitemap_results = self.ping_search_engines(sitemap_url)
                results['sitemap_pings'] = sitemap_results
            
            # Archive and directory submissions for each URL
            archive_tools = ArchiveTools()
            for url in urls:
                # Archive.org save
                archive_result = archive_tools.trigger_archive_save(url)
                results['archive_saves'][url] = archive_result
                
                # Directory submissions
                directory_results = self.submit_to_directories(url)
                results['directory_submissions'][url] = directory_results
                
                time.sleep(1)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Comprehensive ping failed: {str(e)}")
            results['error'] = str(e)
        
        return results
