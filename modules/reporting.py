import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from config import Config
import logging

logger = logging.getLogger(__name__)

class ReportingManager:
    def __init__(self):
        self.config = Config()
        self.campaigns_file = os.path.join(self.config.DATA_DIR, 'campaigns.json')
    
    def generate_analytics_data(self):
        """Generate comprehensive analytics data"""
        try:
            campaigns = self.load_campaigns()
            
            analytics = {
                'overview': self._generate_overview(campaigns),
                'service_performance': self._analyze_service_performance(campaigns),
                'timeline_data': self._generate_timeline_data(campaigns),
                'success_rates': self._calculate_success_rates(campaigns),
                'top_performing_services': self._get_top_services(campaigns),
                'recent_campaigns': self._get_recent_campaigns(campaigns)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            return {}
    
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
    
    def _generate_overview(self, campaigns):
        """Generate overview statistics"""
        total_campaigns = len(campaigns)
        total_urls = sum(campaign.get('total_urls', 0) for campaign in campaigns.values())
        total_successful_pings = sum(campaign.get('successful_pings', 0) for campaign in campaigns.values())
        total_failed_pings = sum(campaign.get('failed_pings', 0) for campaign in campaigns.values())
        
        overall_success_rate = 0
        if total_successful_pings + total_failed_pings > 0:
            overall_success_rate = (total_successful_pings / (total_successful_pings + total_failed_pings)) * 100
        
        # Status distribution
        status_counts = defaultdict(int)
        for campaign in campaigns.values():
            status_counts[campaign.get('status', 'unknown')] += 1
        
        return {
            'total_campaigns': total_campaigns,
            'total_urls': total_urls,
            'total_successful_pings': total_successful_pings,
            'total_failed_pings': total_failed_pings,
            'overall_success_rate': round(overall_success_rate, 2),
            'status_distribution': dict(status_counts)
        }
    
    def _analyze_service_performance(self, campaigns):
        """Analyze performance by service type"""
        service_stats = {
            'rss_services': defaultdict(lambda: {'success': 0, 'total': 0}),
            'search_engines': defaultdict(lambda: {'success': 0, 'total': 0}),
            'archive_services': {'success': 0, 'total': 0},
            'directories': defaultdict(lambda: {'success': 0, 'total': 0})
        }
        
        for campaign in campaigns.values():
            results = campaign.get('results', {})
            
            # RSS service performance
            for feed_type, rss_results in results.get('rss_pings', {}).items():
                for service, result in rss_results.items():
                    service_stats['rss_services'][service]['total'] += 1
                    if result.get('success'):
                        service_stats['rss_services'][service]['success'] += 1
            
            # Search engine performance
            for engine, result in results.get('sitemap_pings', {}).items():
                service_stats['search_engines'][engine]['total'] += 1
                if result.get('success'):
                    service_stats['search_engines'][engine]['success'] += 1
            
            # Archive service performance
            for url, result in results.get('archive_saves', {}).items():
                service_stats['archive_services']['total'] += 1
                if result.get('success'):
                    service_stats['archive_services']['success'] += 1
            
            # Directory performance
            for url, dir_results in results.get('directory_submissions', {}).items():
                for directory, result in dir_results.items():
                    service_stats['directories'][directory]['total'] += 1
                    if result.get('success'):
                        service_stats['directories'][directory]['success'] += 1
        
        # Calculate success rates
        formatted_stats = {}
        
        for service_type, services in service_stats.items():
            if service_type == 'archive_services':
                total = services['total']
                success = services['success']
                rate = (success / total * 100) if total > 0 else 0
                formatted_stats[service_type] = {
                    'success_rate': round(rate, 2),
                    'total_attempts': total,
                    'successful_attempts': success
                }
            else:
                formatted_stats[service_type] = {}
                for service_name, stats in services.items():
                    total = stats['total']
                    success = stats['success']
                    rate = (success / total * 100) if total > 0 else 0
                    formatted_stats[service_type][service_name] = {
                        'success_rate': round(rate, 2),
                        'total_attempts': total,
                        'successful_attempts': success
                    }
        
        return formatted_stats
    
    def _generate_timeline_data(self, campaigns):
        """Generate timeline data for charts"""
        timeline = defaultdict(lambda: {'campaigns': 0, 'urls': 0, 'pings': 0})
        
        for campaign in campaigns.values():
            created_date = campaign.get('created_date', '')
            if created_date:
                try:
                    date = datetime.fromisoformat(created_date).date()
                    date_str = date.strftime('%Y-%m-%d')
                    
                    timeline[date_str]['campaigns'] += 1
                    timeline[date_str]['urls'] += campaign.get('total_urls', 0)
                    timeline[date_str]['pings'] += campaign.get('successful_pings', 0)
                except:
                    continue
        
        # Sort by date and return last 30 days
        sorted_timeline = sorted(timeline.items())
        return dict(sorted_timeline[-30:])  # Last 30 days
    
    def _calculate_success_rates(self, campaigns):
        """Calculate success rates by ping method"""
        method_stats = {
            'rss': {'success': 0, 'total': 0},
            'sitemap': {'success': 0, 'total': 0},
            'archive': {'success': 0, 'total': 0},
            'directories': {'success': 0, 'total': 0}
        }
        
        for campaign in campaigns.values():
            results = campaign.get('results', {})
            
            # RSS method
            for feed_type, rss_results in results.get('rss_pings', {}).items():
                for service, result in rss_results.items():
                    method_stats['rss']['total'] += 1
                    if result.get('success'):
                        method_stats['rss']['success'] += 1
            
            # Sitemap method
            for engine, result in results.get('sitemap_pings', {}).items():
                method_stats['sitemap']['total'] += 1
                if result.get('success'):
                    method_stats['sitemap']['success'] += 1
            
            # Archive method
            for url, result in results.get('archive_saves', {}).items():
                method_stats['archive']['total'] += 1
                if result.get('success'):
                    method_stats['archive']['success'] += 1
            
            # Directories method
            for url, dir_results in results.get('directory_submissions', {}).items():
                for directory, result in dir_results.items():
                    method_stats['directories']['total'] += 1
                    if result.get('success'):
                        method_stats['directories']['success'] += 1
        
        # Calculate rates
        success_rates = {}
        for method, stats in method_stats.items():
            total = stats['total']
            success = stats['success']
            rate = (success / total * 100) if total > 0 else 0
            success_rates[method] = {
                'rate': round(rate, 2),
                'total': total,
                'success': success
            }
        
        return success_rates
    
    def _get_top_services(self, campaigns, limit=10):
        """Get top performing services"""
        service_performance = {}
        
        for campaign in campaigns.values():
            results = campaign.get('results', {})
            
            # Collect all service results
            for feed_type, rss_results in results.get('rss_pings', {}).items():
                for service, result in rss_results.items():
                    if service not in service_performance:
                        service_performance[service] = {'success': 0, 'total': 0, 'type': 'RSS'}
                    service_performance[service]['total'] += 1
                    if result.get('success'):
                        service_performance[service]['success'] += 1
            
            for engine, result in results.get('sitemap_pings', {}).items():
                if engine not in service_performance:
                    service_performance[engine] = {'success': 0, 'total': 0, 'type': 'Search Engine'}
                service_performance[engine]['total'] += 1
                if result.get('success'):
                    service_performance[engine]['success'] += 1
        
        # Calculate success rates and sort
        for service, stats in service_performance.items():
            total = stats['total']
            success = stats['success']
            stats['success_rate'] = (success / total * 100) if total > 0 else 0
        
        # Sort by success rate and total attempts
        sorted_services = sorted(
            service_performance.items(),
            key=lambda x: (x[1]['success_rate'], x[1]['total']),
            reverse=True
        )
        
        return dict(sorted_services[:limit])
    
    def _get_recent_campaigns(self, campaigns, limit=5):
        """Get most recent campaigns"""
        campaign_list = []
        
        for campaign_id, campaign in campaigns.items():
            campaign_data = {
                'id': campaign_id,
                'name': campaign.get('name', 'Unnamed Campaign'),
                'status': campaign.get('status', 'unknown'),
                'created_date': campaign.get('created_date', ''),
                'total_urls': campaign.get('total_urls', 0),
                'successful_pings': campaign.get('successful_pings', 0),
                'failed_pings': campaign.get('failed_pings', 0)
            }
            
            # Calculate success rate
            total_pings = campaign_data['successful_pings'] + campaign_data['failed_pings']
            if total_pings > 0:
                campaign_data['success_rate'] = round(
                    (campaign_data['successful_pings'] / total_pings) * 100, 2
                )
            else:
                campaign_data['success_rate'] = 0
            
            campaign_list.append(campaign_data)
        
        # Sort by creation date (most recent first)
        campaign_list.sort(key=lambda x: x['created_date'], reverse=True)
        
        return campaign_list[:limit]
