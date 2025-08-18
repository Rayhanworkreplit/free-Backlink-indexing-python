import os
import json
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from config import Config
import logging

logger = logging.getLogger(__name__)

class RSSGenerator:
    def __init__(self):
        self.config = Config()
    
    def generate_rss_feed(self, urls, feed_type="general", campaign_id=None):
        """Generate RSS feed for given URLs"""
        try:
            fg = FeedGenerator()
            
            # Set feed metadata
            base_url = "http://localhost:5000"  # In production, use actual domain
            feed_title = f"{self.config.RSS_TITLE_PREFIX} - {feed_type.title()}"
            
            fg.title(feed_title)
            fg.id(f"{base_url}/feeds/{feed_type}/{campaign_id or 'default'}")
            fg.link(href=base_url, rel='alternate')
            fg.description(self.config.RSS_DESCRIPTION)
            fg.language(self.config.RSS_LANGUAGE)
            fg.lastBuildDate(datetime.now(timezone.utc))
            fg.generator('Free Ping Indexer Pro')
            
            # Add URLs as feed entries
            for idx, url in enumerate(urls):
                fe = fg.add_entry()
                fe.id(f"{base_url}/entry/{campaign_id or 'default'}/{idx}")
                fe.title(self._generate_seo_title(url, feed_type))
                fe.link(href=url)
                fe.description(self._generate_seo_description(url, feed_type))
                fe.pubDate(datetime.now(timezone.utc))
                
            # Generate RSS XML
            rss_xml = fg.rss_str(pretty=True)
            
            # Save to file
            filename = f"{feed_type}_{campaign_id or 'default'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
            filepath = os.path.join(self.config.RSS_FEEDS_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(rss_xml)
            
            logger.info(f"Generated RSS feed: {filepath}")
            return filepath, rss_xml.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error generating RSS feed: {str(e)}")
            raise
    
    def _generate_seo_title(self, url, feed_type):
        """Generate SEO-optimized title for RSS entry"""
        domain = url.split('/')[2] if '//' in url else url
        titles = {
            "general": f"Quality Content from {domain}",
            "tech": f"Latest Tech Updates from {domain}",
            "business": f"Business Insights from {domain}",
            "news": f"Breaking News from {domain}",
            "blog": f"Blog Post from {domain}"
        }
        return titles.get(feed_type, f"Content Update from {domain}")
    
    def _generate_seo_description(self, url, feed_type):
        """Generate SEO-optimized description for RSS entry"""
        domain = url.split('/')[2] if '//' in url else url
        descriptions = {
            "general": f"Discover valuable content and insights from {domain}. Stay updated with the latest information.",
            "tech": f"Explore cutting-edge technology articles and updates from {domain}. Tech news and insights.",
            "business": f"Get the latest business news, strategies, and insights from {domain}. Professional content.",
            "news": f"Stay informed with breaking news and current events from {domain}. Latest updates.",
            "blog": f"Read engaging blog posts and articles from {domain}. Quality written content."
        }
        return descriptions.get(feed_type, f"Quality content and updates from {domain}")
    
    def generate_multiple_feeds(self, urls, campaign_id=None):
        """Generate multiple themed RSS feeds"""
        feed_types = ["general", "tech", "business", "news", "blog"]
        generated_feeds = {}
        
        for feed_type in feed_types:
            try:
                filepath, xml_content = self.generate_rss_feed(urls, feed_type, campaign_id)
                generated_feeds[feed_type] = {
                    "filepath": filepath,
                    "xml_content": xml_content,
                    "url": f"http://localhost:5000/feeds/{feed_type}/{campaign_id or 'default'}"
                }
            except Exception as e:
                logger.error(f"Failed to generate {feed_type} feed: {str(e)}")
                generated_feeds[feed_type] = None
        
        return generated_feeds
