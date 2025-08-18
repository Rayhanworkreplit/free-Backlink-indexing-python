import json
import os
import csv
import io
from datetime import datetime
from config import Config
from utils.validators import URLValidator
from modules.webhook_manager import WebhookManager
import logging

logger = logging.getLogger(__name__)

class URLManager:
    def __init__(self):
        self.config = Config()
        self.validator = URLValidator()
        self.webhook_manager = WebhookManager()
        self.campaigns_file = os.path.join(self.config.DATA_DIR, 'campaigns.json')
        self.results_file = os.path.join(self.config.DATA_DIR, 'ping_results.json')
    
    def create_campaign(self, name, urls, ping_methods=None):
        """Create a new ping campaign"""
        try:
            # Validate URLs
            valid_urls = []
            invalid_urls = []
            
            for url in urls:
                if self.validator.is_valid_url(url):
                    clean_url = self.validator.clean_url(url)
                    valid_urls.append(clean_url)
                else:
                    invalid_urls.append(url)
            
            if len(valid_urls) == 0:
                raise ValueError("No valid URLs provided")
            
            if len(valid_urls) > self.config.MAX_URLS_PER_CAMPAIGN:
                raise ValueError(f"Too many URLs. Maximum allowed: {self.config.MAX_URLS_PER_CAMPAIGN}")
            
            # Create campaign
            campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            campaign = {
                'id': campaign_id,
                'name': name,
                'urls': valid_urls,
                'invalid_urls': invalid_urls,
                'ping_methods': ping_methods or ['rss', 'sitemap', 'archive', 'directories'],
                'status': 'pending',
                'created_date': datetime.now().isoformat(),
                'total_urls': len(valid_urls),
                'processed_urls': 0,
                'successful_pings': 0,
                'failed_pings': 0,
                'results': {}
            }
            
            # Save campaign
            campaigns = self.load_campaigns()
            campaigns[campaign_id] = campaign
            self.save_campaigns(campaigns)
            
            logger.info(f"Created campaign {campaign_id} with {len(valid_urls)} URLs")
            return campaign_id, campaign
            
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            raise
    
    def load_campaigns(self):
        """Load campaigns from JSON file"""
        try:
            if os.path.exists(self.campaigns_file):
                with open(self.campaigns_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading campaigns: {str(e)}")
            return {}
    
    def save_campaigns(self, campaigns):
        """Save campaigns to JSON file"""
        try:
            with open(self.campaigns_file, 'w') as f:
                json.dump(campaigns, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving campaigns: {str(e)}")
    
    def get_campaign(self, campaign_id):
        """Get specific campaign by ID"""
        campaigns = self.load_campaigns()
        return campaigns.get(campaign_id)
    
    def update_campaign_status(self, campaign_id, status, results=None):
        """Update campaign status and results"""
        try:
            campaigns = self.load_campaigns()
            if campaign_id in campaigns:
                campaigns[campaign_id]['status'] = status
                campaigns[campaign_id]['last_updated'] = datetime.now().isoformat()
                
                if results:
                    campaigns[campaign_id]['results'] = results
                    # Update statistics
                    self._update_campaign_stats(campaigns[campaign_id], results)
                
                self.save_campaigns(campaigns)
                logger.info(f"Updated campaign {campaign_id} status to {status}")
                
                # Send webhook notification for completed campaigns
                if status == 'completed' and results:
                    try:
                        self.webhook_manager.send_hashnode_notification(
                            campaign_id, campaigns[campaign_id], results
                        )
                    except Exception as webhook_error:
                        logger.warning(f"Webhook notification failed: {str(webhook_error)}")
            
        except Exception as e:
            logger.error(f"Error updating campaign status: {str(e)}")
    
    def _update_campaign_stats(self, campaign, results):
        """Update campaign statistics based on results"""
        try:
            successful_pings = 0
            failed_pings = 0
            
            # Count RSS ping successes
            for feed_type, rss_results in results.get('rss_pings', {}).items():
                for service, result in rss_results.items():
                    if result.get('success'):
                        successful_pings += 1
                    else:
                        failed_pings += 1
            
            # Count sitemap ping successes
            for engine, result in results.get('sitemap_pings', {}).items():
                if result.get('success'):
                    successful_pings += 1
                else:
                    failed_pings += 1
            
            # Count archive saves
            for url, result in results.get('archive_saves', {}).items():
                if result.get('success'):
                    successful_pings += 1
                else:
                    failed_pings += 1
            
            # Count directory submissions
            for url, dir_results in results.get('directory_submissions', {}).items():
                for directory, result in dir_results.items():
                    if result.get('success'):
                        successful_pings += 1
                    else:
                        failed_pings += 1
            
            campaign['successful_pings'] = successful_pings
            campaign['failed_pings'] = failed_pings
            campaign['processed_urls'] = len(campaign['urls'])
            
        except Exception as e:
            logger.error(f"Error updating campaign stats: {str(e)}")
    
    def parse_bulk_urls(self, content, format_type='text'):
        """Parse URLs from bulk input"""
        urls = []
        
        try:
            if format_type == 'csv':
                # Parse CSV content
                csv_reader = csv.reader(io.StringIO(content))
                for row in csv_reader:
                    if row:  # Skip empty rows
                        url = row[0].strip()  # Take first column
                        if url and not url.startswith('#'):  # Skip comments
                            urls.append(url)
            
            else:  # text format
                # Split by lines and clean up
                lines = content.split('\n')
                for line in lines:
                    url = line.strip()
                    if url and not url.startswith('#'):  # Skip empty lines and comments
                        urls.append(url)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_urls = []
            for url in urls:
                if url not in seen:
                    seen.add(url)
                    unique_urls.append(url)
            
            logger.info(f"Parsed {len(unique_urls)} unique URLs from {format_type} input")
            return unique_urls
            
        except Exception as e:
            logger.error(f"Error parsing bulk URLs: {str(e)}")
            raise
    
    def export_results(self, campaign_id, format_type='csv'):
        """Export campaign results"""
        try:
            campaign = self.get_campaign(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            if format_type == 'csv':
                return self._export_csv(campaign)
            elif format_type == 'json':
                return self._export_json(campaign)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            logger.error(f"Error exporting results: {str(e)}")
            raise
    
    def _export_csv(self, campaign):
        """Export campaign results as CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Campaign ID', 'Campaign Name', 'URL', 'Service Type', 
            'Service Name', 'Success', 'Status Code', 'Timestamp'
        ])
        
        results = campaign.get('results', {})
        
        # RSS ping results
        for feed_type, rss_results in results.get('rss_pings', {}).items():
            for service, result in rss_results.items():
                writer.writerow([
                    campaign['id'], campaign['name'], 'RSS Feed',
                    f'RSS ({feed_type})', service, result.get('success', False),
                    result.get('status_code', ''), result.get('timestamp', '')
                ])
        
        # Sitemap ping results
        for engine, result in results.get('sitemap_pings', {}).items():
            writer.writerow([
                campaign['id'], campaign['name'], 'Sitemap',
                'Search Engine', engine, result.get('success', False),
                result.get('status_code', ''), result.get('timestamp', '')
            ])
        
        # Archive results
        for url, result in results.get('archive_saves', {}).items():
            writer.writerow([
                campaign['id'], campaign['name'], url,
                'Archive', 'Archive.org', result.get('success', False),
                result.get('status_code', ''), result.get('timestamp', '')
            ])
        
        # Directory submission results
        for url, dir_results in results.get('directory_submissions', {}).items():
            for directory, result in dir_results.items():
                writer.writerow([
                    campaign['id'], campaign['name'], url,
                    'Directory', directory, result.get('success', False),
                    result.get('status_code', ''), result.get('timestamp', '')
                ])
        
        return output.getvalue()
    
    def _export_json(self, campaign):
        """Export campaign results as JSON"""
        return json.dumps(campaign, indent=2)
