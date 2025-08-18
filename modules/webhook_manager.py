"""
Webhook Manager for external service notifications
Handles Hashnode webhooks and other notification systems
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class WebhookManager:
    def __init__(self):
        self.webhooks = {
            'hashnode': {
                'url': 'https://linkindex.hashnode.dev/linkindex',
                'token': 'hn_whs_HvbYt7lsSntJNWIKu3MjX8WJU',
                'enabled': True
            }
        }
        
    def send_hashnode_notification(self, campaign_id: str, campaign_data: Dict, results: Dict) -> bool:
        """
        Send notification to Hashnode webhook when campaign completes
        
        Args:
            campaign_id: Campaign identifier
            campaign_data: Campaign information
            results: Ping results
            
        Returns:
            bool: Success status
        """
        try:
            if not self.webhooks['hashnode']['enabled']:
                logger.info("Hashnode webhook is disabled")
                return False
                
            webhook_url = self.webhooks['hashnode']['url']
            webhook_token = self.webhooks['hashnode']['token']
            
            # Prepare payload
            payload = {
                'event': 'campaign_completed',
                'timestamp': datetime.now().isoformat(),
                'campaign': {
                    'id': campaign_id,
                    'name': campaign_data.get('name', 'Unnamed Campaign'),
                    'status': campaign_data.get('status', 'unknown'),
                    'total_urls': campaign_data.get('total_urls', 0),
                    'successful_pings': campaign_data.get('successful_pings', 0),
                    'failed_pings': campaign_data.get('failed_pings', 0),
                    'ping_methods': campaign_data.get('ping_methods', []),
                    'created_date': campaign_data.get('created_date')
                },
                'results_summary': self._generate_results_summary(results),
                'urls': campaign_data.get('urls', [])[:10]  # Limit to first 10 URLs
            }
            
            # Add authentication header
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {webhook_token}',
                'User-Agent': 'Free-Ping-Indexer-Pro/1.0'
            }
            
            # Send webhook
            response = requests.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Hashnode webhook sent successfully for campaign {campaign_id}")
                return True
            else:
                logger.warning(f"Hashnode webhook failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Hashnode webhook request failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Hashnode webhook: {str(e)}")
            return False
    
    def _generate_results_summary(self, results: Dict) -> Dict:
        """Generate summary statistics from ping results"""
        summary = {
            'rss_services': {'total': 0, 'successful': 0},
            'search_engines': {'total': 0, 'successful': 0},
            'archive_saves': {'total': 0, 'successful': 0},
            'directory_submissions': {'total': 0, 'successful': 0}
        }
        
        # RSS results
        for feed_type, rss_results in results.get('rss_pings', {}).items():
            for service, result in rss_results.items():
                summary['rss_services']['total'] += 1
                if result.get('success'):
                    summary['rss_services']['successful'] += 1
        
        # Search engine results
        for engine, result in results.get('sitemap_pings', {}).items():
            summary['search_engines']['total'] += 1
            if result.get('success'):
                summary['search_engines']['successful'] += 1
        
        # Archive results
        for url, result in results.get('archive_saves', {}).items():
            summary['archive_saves']['total'] += 1
            if result.get('success'):
                summary['archive_saves']['successful'] += 1
        
        # Directory results
        for url, dir_results in results.get('directory_submissions', {}).items():
            for directory, result in dir_results.items():
                summary['directory_submissions']['total'] += 1
                if result.get('success'):
                    summary['directory_submissions']['successful'] += 1
        
        # Calculate success rates
        for service_type in summary:
            total = summary[service_type]['total']
            successful = summary[service_type]['successful']
            rate = (successful / total * 100) if total > 0 else 0.0
            summary[service_type]['success_rate'] = round(rate, 2)
        
        return summary
    
    def send_bulk_notification(self, campaigns: List[Dict]) -> Dict:
        """
        Send bulk notification for multiple completed campaigns
        
        Args:
            campaigns: List of campaign data
            
        Returns:
            Dict: Results summary
        """
        results = {
            'total_campaigns': len(campaigns),
            'successful_notifications': 0,
            'failed_notifications': 0,
            'errors': []
        }
        
        for campaign in campaigns:
            try:
                success = self.send_hashnode_notification(
                    campaign['id'],
                    campaign,
                    campaign.get('results', {})
                )
                
                if success:
                    results['successful_notifications'] += 1
                else:
                    results['failed_notifications'] += 1
                    
            except Exception as e:
                results['failed_notifications'] += 1
                results['errors'].append(f"Campaign {campaign['id']}: {str(e)}")
                logger.error(f"Bulk notification error for {campaign['id']}: {str(e)}")
        
        return results
    
    def test_webhook_connection(self, webhook_name: str = 'hashnode') -> Dict:
        """
        Test webhook connection
        
        Args:
            webhook_name: Name of webhook to test
            
        Returns:
            Dict: Test results
        """
        if webhook_name not in self.webhooks:
            return {
                'success': False,
                'error': f"Webhook '{webhook_name}' not configured"
            }
        
        webhook = self.webhooks[webhook_name]
        
        try:
            # Send test payload
            test_payload = {
                'event': 'test_connection',
                'timestamp': datetime.now().isoformat(),
                'message': 'Free Ping Indexer Pro webhook test'
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {webhook["token"]}',
                'User-Agent': 'Free-Ping-Indexer-Pro/1.0'
            }
            
            response = requests.post(
                webhook['url'],
                json=test_payload,
                headers=headers,
                timeout=15
            )
            
            return {
                'success': response.status_code in [200, 201, 204],
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'response_text': response.text[:200] if response.text else None
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_webhook_config(self, webhook_name: str, config: Dict) -> bool:
        """
        Update webhook configuration
        
        Args:
            webhook_name: Name of webhook
            config: New configuration
            
        Returns:
            bool: Success status
        """
        try:
            if webhook_name in self.webhooks:
                self.webhooks[webhook_name].update(config)
                logger.info(f"Updated webhook config for {webhook_name}")
                return True
            else:
                self.webhooks[webhook_name] = config
                logger.info(f"Added new webhook config for {webhook_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update webhook config: {str(e)}")
            return False
    
    def get_webhook_status(self) -> Dict:
        """Get status of all configured webhooks"""
        status = {}
        
        for name, config in self.webhooks.items():
            status[name] = {
                'enabled': config.get('enabled', False),
                'url': config.get('url', ''),
                'last_test': None  # Would be stored in database in real implementation
            }
        
        return status