import os
import json
from datetime import datetime
from config import Config
import logging

logger = logging.getLogger(__name__)

class SitemapManager:
    def __init__(self):
        self.config = Config()
    
    def create_sitemap(self, urls, campaign_id=None):
        """Create XML sitemap for given URLs"""
        try:
            sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
            sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            
            current_time = datetime.now().isoformat()
            
            for url in urls:
                sitemap_xml += f"""  <url>
    <loc>{url}</loc>
    <lastmod>{current_time}</lastmod>
    <changefreq>{self.config.SITEMAP_CHANGEFREQ}</changefreq>
    <priority>{self.config.SITEMAP_PRIORITY}</priority>
  </url>
"""
            
            sitemap_xml += '</urlset>'
            
            # Save sitemap to file
            filename = f"sitemap_{campaign_id or 'default'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
            filepath = os.path.join(self.config.SITEMAPS_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(sitemap_xml)
            
            # Return public URL for the sitemap
            sitemap_url = f"http://localhost:5000/sitemaps/{filename}"
            logger.info(f"Created sitemap: {sitemap_url}")
            
            return sitemap_url
            
        except Exception as e:
            logger.error(f"Error creating sitemap: {str(e)}")
            return None
    
    def create_sitemap_index(self, sitemap_urls):
        """Create sitemap index file for multiple sitemaps"""
        try:
            index_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
            index_xml += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            
            current_time = datetime.now().isoformat()
            
            for sitemap_url in sitemap_urls:
                index_xml += f"""  <sitemap>
    <loc>{sitemap_url}</loc>
    <lastmod>{current_time}</lastmod>
  </sitemap>
"""
            
            index_xml += '</sitemapindex>'
            
            # Save sitemap index
            filename = f"sitemap_index_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
            filepath = os.path.join(self.config.SITEMAPS_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(index_xml)
            
            index_url = f"http://localhost:5000/sitemaps/{filename}"
            logger.info(f"Created sitemap index: {index_url}")
            
            return index_url
            
        except Exception as e:
            logger.error(f"Error creating sitemap index: {str(e)}")
            return None
    
    def validate_sitemap(self, sitemap_content):
        """Validate sitemap XML structure"""
        try:
            # Basic validation - check for required elements
            required_elements = ['<?xml', '<urlset', '<url>', '<loc>']
            for element in required_elements:
                if element not in sitemap_content:
                    return False, f"Missing required element: {element}"
            
            return True, "Sitemap is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
