"""
Live Progress Tracking Module
Provides real-time updates for ping campaigns with detailed progress information
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class LiveProgressTracker:
    def __init__(self):
        self.active_campaigns = {}
        self.campaign_lock = threading.Lock()
        
    def start_campaign(self, campaign_id: str, total_services: int, total_urls: int) -> None:
        """Initialize a new campaign for tracking"""
        with self.campaign_lock:
            self.active_campaigns[campaign_id] = {
                'id': campaign_id,
                'start_time': datetime.now(),
                'total_services': total_services,
                'total_urls': total_urls,
                'total_pings': total_services * total_urls,
                'processed_pings': 0,
                'successful_pings': 0,
                'failed_pings': 0,
                'current_service': '',
                'current_url': '',
                'recent_activities': [],
                'service_results': {},
                'status': 'running',
                'estimated_completion': None,
                'processing_rate': 0  # pings per second
            }
    
    def update_progress(self, campaign_id: str, service: str, url: str, success: bool, response_time: float = 0) -> None:
        """Update campaign progress with a new ping result"""
        if campaign_id not in self.active_campaigns:
            return
            
        with self.campaign_lock:
            campaign = self.active_campaigns[campaign_id]
            
            # Update basic counters
            campaign['processed_pings'] += 1
            if success:
                campaign['successful_pings'] += 1
            else:
                campaign['failed_pings'] += 1
                
            # Update current processing info
            campaign['current_service'] = service
            campaign['current_url'] = url
            
            # Track service-specific results
            if service not in campaign['service_results']:
                campaign['service_results'][service] = {'attempts': 0, 'successes': 0, 'total_time': 0}
            
            service_result = campaign['service_results'][service]
            service_result['attempts'] += 1
            service_result['total_time'] += response_time
            if success:
                service_result['successes'] += 1
            
            # Add to recent activities (keep last 10)
            activity = {
                'service': service,
                'url': url,
                'success': success,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'response_time': response_time
            }
            campaign['recent_activities'].insert(0, activity)
            if len(campaign['recent_activities']) > 10:
                campaign['recent_activities'] = campaign['recent_activities'][:10]
            
            # Calculate processing rate and estimated completion
            elapsed_time = (datetime.now() - campaign['start_time']).total_seconds()
            if elapsed_time > 0:
                campaign['processing_rate'] = campaign['processed_pings'] / elapsed_time
                
                remaining_pings = campaign['total_pings'] - campaign['processed_pings']
                if campaign['processing_rate'] > 0:
                    estimated_seconds = remaining_pings / campaign['processing_rate']
                    campaign['estimated_completion'] = datetime.now() + timedelta(seconds=estimated_seconds)
    
    def get_campaign_progress(self, campaign_id: str) -> Optional[Dict]:
        """Get current progress for a campaign"""
        if campaign_id not in self.active_campaigns:
            return None
            
        with self.campaign_lock:
            campaign = self.active_campaigns[campaign_id].copy()
            
            # Calculate percentage
            if campaign['total_pings'] > 0:
                percentage = (campaign['processed_pings'] / campaign['total_pings']) * 100
            else:
                percentage = 0
                
            # Format estimated time remaining
            estimated_time_remaining = "Unknown"
            if campaign.get('estimated_completion'):
                remaining = campaign['estimated_completion'] - datetime.now()
                if remaining.total_seconds() > 0:
                    minutes = int(remaining.total_seconds() // 60)
                    seconds = int(remaining.total_seconds() % 60)
                    if minutes > 0:
                        estimated_time_remaining = f"{minutes}m {seconds}s"
                    else:
                        estimated_time_remaining = f"{seconds}s"
                else:
                    estimated_time_remaining = "Almost done"
            
            # Calculate success rate
            success_rate = 0
            if campaign['processed_pings'] > 0:
                success_rate = (campaign['successful_pings'] / campaign['processed_pings']) * 100
            
            return {
                'id': campaign_id,
                'percentage': round(percentage, 1),
                'processed': campaign['processed_pings'],
                'total': campaign['total_pings'],
                'successful': campaign['successful_pings'],
                'failed': campaign['failed_pings'],
                'pending': campaign['total_pings'] - campaign['processed_pings'],
                'success_rate': round(success_rate, 1),
                'current_service': campaign.get('current_service', ''),
                'current_url': campaign.get('current_url', ''),
                'recent_activities': campaign.get('recent_activities', []),
                'estimated_time_remaining': estimated_time_remaining,
                'processing_rate': round(campaign.get('processing_rate', 0), 2),
                'status': campaign.get('status', 'running'),
                'elapsed_time': self._format_elapsed_time(campaign['start_time']),
                'service_breakdown': self._get_service_breakdown(campaign['service_results'])
            }
    
    def complete_campaign(self, campaign_id: str) -> None:
        """Mark a campaign as completed"""
        if campaign_id in self.active_campaigns:
            with self.campaign_lock:
                self.active_campaigns[campaign_id]['status'] = 'completed'
                self.active_campaigns[campaign_id]['end_time'] = datetime.now()
    
    def cleanup_old_campaigns(self, max_age_hours: int = 24) -> None:
        """Remove campaigns older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        with self.campaign_lock:
            campaigns_to_remove = []
            for campaign_id, campaign in self.active_campaigns.items():
                if campaign['start_time'] < cutoff_time:
                    campaigns_to_remove.append(campaign_id)
            
            for campaign_id in campaigns_to_remove:
                del self.active_campaigns[campaign_id]
    
    def get_all_active_campaigns(self) -> Dict:
        """Get summary of all active campaigns"""
        with self.campaign_lock:
            return {
                campaign_id: {
                    'id': campaign_id,
                    'status': campaign.get('status', 'unknown'),
                    'start_time': campaign['start_time'].isoformat(),
                    'progress': round((campaign['processed_pings'] / campaign['total_pings'] * 100) if campaign['total_pings'] > 0 else 0, 1)
                }
                for campaign_id, campaign in self.active_campaigns.items()
            }
    
    def _format_elapsed_time(self, start_time: datetime) -> str:
        """Format elapsed time as human-readable string"""
        elapsed = datetime.now() - start_time
        total_seconds = int(elapsed.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _get_service_breakdown(self, service_results: Dict) -> List[Dict]:
        """Get breakdown of results by service"""
        breakdown = []
        for service, results in service_results.items():
            success_rate = (results['successes'] / results['attempts'] * 100) if results['attempts'] > 0 else 0
            avg_response_time = (results['total_time'] / results['attempts']) if results['attempts'] > 0 else 0
            
            breakdown.append({
                'service': service,
                'attempts': results['attempts'],
                'successes': results['successes'],
                'success_rate': round(success_rate, 1),
                'avg_response_time': round(avg_response_time, 3)
            })
        
        return sorted(breakdown, key=lambda x: x['success_rate'], reverse=True)

# Global progress tracker instance
live_progress_tracker = LiveProgressTracker()