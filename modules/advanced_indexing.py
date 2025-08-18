import json
import requests
import logging
import time
import random
from datetime import datetime, timedelta
from feedgen.feed import FeedGenerator
from feedgen.entry import FeedEntry
import tempfile
import os
from config import Config

logger = logging.getLogger(__name__)

class AdvancedIndexingMethods:
    """
    Advanced backlink indexing methods beyond traditional RSS/sitemap pings
    Implements JavaScript heartbeat crawls, distributed crawling, and podcast feed submission
    """
    
    def __init__(self):
        self.config = Config()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:109.0) Gecko/109.0 Firefox/120.0'
        ]
        self.podcast_directories = [
            'https://podcastsconnect.apple.com/api/submit',
            'https://podcasters.spotify.com/pod/submit',
            'https://play.google.com/podcasts/submit',
            'https://www.podcastone.com/submit',
            'https://www.stitcher.com/content-providers',
            'https://www.spreaker.com/cms/podcast/submit',
            'https://tunein.com/podcasts/submit/'
        ]
    
    def generate_heartbeat_script(self, backlink_urls, output_path="static/js/heartbeat.js"):
        """
        Generate JavaScript heartbeat crawler script for high-authority domain deployment
        """
        try:
            # Randomize URLs to avoid patterns
            randomized_urls = random.sample(backlink_urls, min(len(backlink_urls), 50))
            
            js_script = f"""
// Backlink Indexing Heartbeat v1.0
// Deploy this script on high-authority domains for enhanced crawling
(function() {{
    'use strict';
    
    const BACKLINK_URLS = {json.dumps(randomized_urls)};
    const HEARTBEAT_INTERVAL = {random.randint(300000, 900000)}; // 5-15 minutes
    const BATCH_SIZE = 3;
    let currentIndex = 0;
    
    function shuffleArray(array) {{
        for (let i = array.length - 1; i > 0; i--) {{
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }}
        return array;
    }}
    
    function performHeartbeat() {{
        if (currentIndex >= BACKLINK_URLS.length) {{
            currentIndex = 0;
            shuffleArray(BACKLINK_URLS);
        }}
        
        const batch = BACKLINK_URLS.slice(currentIndex, currentIndex + BATCH_SIZE);
        currentIndex += BATCH_SIZE;
        
        batch.forEach((url, index) => {{
            setTimeout(() => {{
                fetch(url, {{
                    method: 'HEAD',
                    mode: 'no-cors',
                    cache: 'no-cache',
                    headers: {{
                        'User-Agent': 'HeartbeatCrawler/1.0',
                        'X-Heartbeat': 'indexing-signal'
                    }}
                }}).catch(() => {{
                    // Silent fail - we just want the request to be made
                }});
                
                console.log(`Heartbeat ping: ${{url}}`);
            }}, index * {random.randint(2000, 5000)});
        }});
    }}
    
    // Initial heartbeat after page load
    window.addEventListener('load', () => {{
        setTimeout(performHeartbeat, {random.randint(10000, 30000)});
    }});
    
    // Regular heartbeat interval
    setInterval(performHeartbeat, HEARTBEAT_INTERVAL);
    
    // Heartbeat on user interactions
    ['click', 'scroll', 'keydown'].forEach(event => {{
        document.addEventListener(event, () => {{
            if (Math.random() < 0.1) {{ // 10% chance
                setTimeout(performHeartbeat, {random.randint(1000, 5000)});
            }}
        }});
    }});
}})();
"""
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(js_script)
            
            logger.info(f"Generated heartbeat script with {len(randomized_urls)} URLs")
            return {
                'success': True,
                'script_path': output_path,
                'urls_count': len(randomized_urls),
                'timestamp': datetime.now().isoformat(),
                'deployment_instructions': {
                    'embed_code': f'<script src="{output_path}" async></script>',
                    'cdn_suggestion': 'Deploy on high-authority domains or CDN for maximum effect'
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate heartbeat script: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def simulate_distributed_crawling(self, backlink_urls, crawl_count=20, use_proxy_rotation=False):
        """
        Advanced distributed crawling with professional proxy rotation support
        """
        from modules.proxy_rotation import ProxyRotationManager
        
        results = {
            'total_crawls': 0,
            'successful_crawls': 0,
            'failed_crawls': 0,
            'crawl_details': [],
            'ip_addresses_used': set(),
            'timestamp': datetime.now().isoformat(),
            'proxy_rotation_enabled': use_proxy_rotation
        }
        
        # Initialize proxy rotation manager
        rotation_manager = ProxyRotationManager() if use_proxy_rotation else None
        
        try:
            # Randomize URLs and limit batch size
            urls_to_crawl = random.sample(backlink_urls, min(len(backlink_urls), crawl_count))
            logger.info(f"Starting distributed crawling of {len(urls_to_crawl)} URLs")
            
            for i, url in enumerate(urls_to_crawl):
                # Progressive delay with jitter
                if i > 0:
                    base_delay = 3.0 + (i * 0.2)  # Gradually increase delays
                    delay = base_delay + random.uniform(-1.0, 2.0)
                    time.sleep(max(1.0, delay))
                
                try:
                    if use_proxy_rotation and rotation_manager:
                        # Use professional proxy rotation
                        result = rotation_manager.make_rotating_request(url, method='HEAD')
                        
                        if result['success']:
                            response = result['response']
                            headers_used = result['headers_used']
                            
                            # Try to extract IP information if available
                            current_ip = 'proxy-hidden'
                            try:
                                # Make a quick IP check (optional)
                                ip_check = rotation_manager.make_rotating_request('http://httpbin.org/ip', method='GET')
                                if ip_check['success']:
                                    current_ip = ip_check['response'].json().get('origin', 'unknown')
                                    results['ip_addresses_used'].add(current_ip)
                            except:
                                pass
                            
                            crawl_detail = {
                                'url': url,
                                'success': True,
                                'status_code': response.status_code,
                                'method': 'HEAD',
                                'user_agent': headers_used.get('User-Agent', '')[:50] + '...',
                                'response_time': response.elapsed.total_seconds() if hasattr(response, 'elapsed') and hasattr(response.elapsed, 'total_seconds') else 0,
                                'ip_address': current_ip,
                                'proxy_used': True,
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            results['successful_crawls'] += 1
                            logger.info(f"Proxy crawl success: {url} ({response.status_code}) via {current_ip}")
                        else:
                            crawl_detail = {
                                'url': url,
                                'success': False,
                                'error': result.get('error', 'Unknown error'),
                                'proxy_used': True,
                                'timestamp': datetime.now().isoformat()
                            }
                            results['failed_crawls'] += 1
                            logger.warning(f"Proxy crawl failed: {url}")
                    
                    else:
                        # Standard crawling with enhanced User-Agent rotation
                        user_agent = random.choice(self.user_agents)
                        headers = {
                            'User-Agent': user_agent,
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.9', 'en-CA,en;q=0.9', 'en-AU,en;q=0.8']),
                            'Accept-Encoding': 'gzip, deflate, br',
                            'DNT': random.choice(['1', '0']),
                            'Connection': 'keep-alive',
                            'Cache-Control': random.choice(['no-cache', 'max-age=0']),
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Site': 'none'
                        }
                        
                        # Vary request methods intelligently
                        method = 'HEAD' if random.random() < 0.8 else 'GET'
                        
                        if method == 'GET':
                            response = requests.get(url, headers=headers, timeout=12, allow_redirects=True)
                        else:
                            response = requests.head(url, headers=headers, timeout=8, allow_redirects=True)
                        
                        success = response.status_code in [200, 201, 202, 301, 302, 304]
                        
                        crawl_detail = {
                            'url': url,
                            'success': success,
                            'status_code': response.status_code,
                            'method': method,
                            'user_agent': user_agent[:50] + '...',
                            'response_time': response.elapsed.total_seconds(),
                            'proxy_used': False,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        if success:
                            results['successful_crawls'] += 1
                            logger.info(f"Standard crawl success: {url} ({response.status_code})")
                        else:
                            results['failed_crawls'] += 1
                            logger.warning(f"Standard crawl failed: {url} ({response.status_code})")
                    
                    results['crawl_details'].append(crawl_detail)
                    results['total_crawls'] += 1
                
                except Exception as e:
                    results['total_crawls'] += 1
                    results['failed_crawls'] += 1
                    
                    crawl_detail = {
                        'url': url,
                        'success': False,
                        'error': str(e),
                        'proxy_used': use_proxy_rotation,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    results['crawl_details'].append(crawl_detail)
                    logger.error(f"Crawl error for {url}: {str(e)}")
            
            # Convert set to list for JSON serialization
            results['ip_addresses_used'] = list(results['ip_addresses_used'])
            results['unique_ips_count'] = len(results['ip_addresses_used'])
            
        except Exception as e:
            logger.error(f"Distributed crawling failed: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def generate_podcast_feed(self, backlink_urls, campaign_id=None):
        """
        Generate podcast RSS feed with backlinks embedded in episode descriptions
        """
        try:
            # Create podcast feed
            fg = FeedGenerator()
            fg.title(f'SEO Discovery Podcast - Campaign {campaign_id or "Default"}')
            fg.description('Advanced backlink indexing through podcast feed distribution')
            fg.link(href='http://localhost:5000', rel='alternate')
            fg.language('en-US')
            fg.author(name='Free Ping Indexer Pro', email='noreply@localhost')
            fg.category(category='Technology')
            fg.image(url='http://localhost:5000/static/podcast-cover.jpg', 
                    title='SEO Discovery Podcast',
                    link='http://localhost:5000')
            
            # Create episodes with backlinks in descriptions
            episode_count = min(len(backlink_urls), 20)  # Limit episodes
            urls_per_episode = max(1, len(backlink_urls) // episode_count)
            
            for i in range(episode_count):
                start_idx = i * urls_per_episode
                end_idx = min(start_idx + urls_per_episode, len(backlink_urls))
                episode_urls = backlink_urls[start_idx:end_idx]
                
                fe = fg.add_entry()
                fe.title(f'Discovery Episode {i + 1}: Quality Content Resources')
                
                # Embed URLs in description with natural language
                description_parts = [
                    f"In this episode, we explore valuable web resources and quality content:",
                    ""
                ]
                
                for j, url in enumerate(episode_urls):
                    description_parts.append(f"Resource {j + 1}: {url}")
                    description_parts.append(f"Visit this comprehensive resource at {url} for detailed information.")
                    description_parts.append("")
                
                description_parts.extend([
                    "These resources provide valuable insights and information for our listeners.",
                    "Each link has been carefully curated for quality and relevance."
                ])
                
                fe.description('\n'.join(description_parts))
                fe.link(href=episode_urls[0] if episode_urls else 'http://localhost:5000')
                fe.guid(f'episode-{campaign_id or "default"}-{i + 1}')
                fe.pubDate(datetime.now() - timedelta(days=episode_count - i))
            
            # Generate RSS feed file
            feed_filename = f'podcast_feed_{campaign_id or "default"}_{int(time.time())}.xml'
            feed_path = os.path.join('data/rss_feeds', feed_filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(feed_path), exist_ok=True)
            
            # Write feed to file
            fg.rss_file(feed_path)
            
            logger.info(f"Generated podcast feed with {episode_count} episodes")
            
            return {
                'success': True,
                'feed_path': feed_path,
                'feed_url': f'http://localhost:5000/{feed_path}',
                'episode_count': episode_count,
                'urls_included': len(backlink_urls),
                'timestamp': datetime.now().isoformat(),
                'submission_targets': self.podcast_directories
            }
            
        except Exception as e:
            logger.error(f"Failed to generate podcast feed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def submit_podcast_feed(self, feed_url, podcast_title="SEO Discovery Podcast"):
        """
        Submit podcast feed to directories (simulated - actual submission requires manual process)
        """
        results = {
            'submitted_to': [],
            'submission_instructions': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Note: Most podcast directories require manual submission or API keys
        # This provides instructions for manual submission
        
        for directory in self.podcast_directories:
            directory_name = directory.split('//')[1].split('/')[0]
            
            results['submitted_to'].append(directory_name)
            results['submission_instructions'][directory_name] = {
                'url': directory,
                'feed_url': feed_url,
                'title': podcast_title,
                'manual_steps': [
                    f"1. Visit {directory}",
                    f"2. Submit feed URL: {feed_url}",
                    f"3. Use title: {podcast_title}",
                    "4. Complete manual verification process"
                ]
            }
        
        logger.info(f"Generated submission instructions for {len(self.podcast_directories)} directories")
        return results
    
    def comprehensive_advanced_indexing(self, backlink_urls, campaign_id=None):
        """
        Execute comprehensive advanced indexing strategy
        """
        results = {
            'campaign_id': campaign_id,
            'urls_count': len(backlink_urls),
            'timestamp': datetime.now().isoformat(),
            'heartbeat_script': {},
            'distributed_crawling': {},
            'podcast_feed': {},
            'podcast_submission': {}
        }
        
        try:
            logger.info(f"Starting advanced indexing for {len(backlink_urls)} URLs")
            
            # Generate JavaScript heartbeat script
            heartbeat_result = self.generate_heartbeat_script(backlink_urls)
            results['heartbeat_script'] = heartbeat_result
            
            # Perform distributed crawling simulation
            crawling_result = self.simulate_distributed_crawling(backlink_urls, crawl_count=15)
            results['distributed_crawling'] = crawling_result
            
            # Generate podcast feed
            podcast_result = self.generate_podcast_feed(backlink_urls, campaign_id)
            results['podcast_feed'] = podcast_result
            
            # Generate podcast submission instructions
            if podcast_result.get('success'):
                submission_result = self.submit_podcast_feed(
                    podcast_result['feed_url'],
                    f"SEO Discovery Podcast - Campaign {campaign_id or 'Default'}"
                )
                results['podcast_submission'] = submission_result
            
            logger.info("Advanced indexing methods completed successfully")
            
        except Exception as e:
            logger.error(f"Advanced indexing failed: {str(e)}")
            results['error'] = str(e)
        
        return results