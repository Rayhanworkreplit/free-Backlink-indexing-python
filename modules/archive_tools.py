import requests
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class ArchiveTools:
    def __init__(self):
        self.config = Config()
    
    def trigger_archive_save(self, url):
        """Trigger Archive.org Wayback Machine save"""
        try:
            archive_url = f"https://web.archive.org/save/{url}"
            logger.info(f"Triggering archive save for: {url}")
            
            response = requests.get(
                archive_url,
                timeout=self.config.ARCHIVE_PING_TIMEOUT,
                headers={
                    'User-Agent': 'Free Ping Indexer Pro/1.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
            )
            
            success = response.status_code in [200, 201, 202]
            
            result = {
                'success': success,
                'status_code': response.status_code,
                'archive_url': archive_url,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                # Try to extract the archived URL from response
                try:
                    archived_url = f"https://web.archive.org/web/{datetime.now().strftime('%Y%m%d%H%M%S')}/{url}"
                    result['archived_url'] = archived_url
                except:
                    pass
            
            logger.info(f"Archive save result for {url}: {success}")
            return result
            
        except Exception as e:
            logger.error(f"Archive save failed for {url}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_archive_status(self, url):
        """Check if URL is archived in Wayback Machine"""
        try:
            check_url = f"https://archive.org/wayback/available?url={url}"
            response = requests.get(check_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                archived_snapshots = data.get('archived_snapshots', {})
                closest = archived_snapshots.get('closest', {})
                
                if closest and closest.get('available'):
                    return {
                        'archived': True,
                        'archive_url': closest.get('url'),
                        'timestamp': closest.get('timestamp')
                    }
            
            return {'archived': False}
            
        except Exception as e:
            logger.error(f"Archive status check failed for {url}: {str(e)}")
            return {'archived': False, 'error': str(e)}
    
    def bulk_archive_save(self, urls):
        """Trigger archive saves for multiple URLs"""
        results = {}
        
        for url in urls:
            result = self.trigger_archive_save(url)
            results[url] = result
            
            # Rate limiting - be respectful to Archive.org
            import time
            time.sleep(3)
        
        return results
