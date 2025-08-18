import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from modules.ping_services import PingServices
from modules.url_manager import URLManager

logger = logging.getLogger(__name__)

class PingScheduler:
    def __init__(self):
        self.ping_services = PingServices()
        self.url_manager = URLManager()
        self.scheduler_thread = None
        self.is_running = False
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Ping scheduler started")
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Ping scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)
    
    def schedule_campaign(self, campaign_id, schedule_type='immediate', schedule_time=None):
        """Schedule a campaign for execution"""
        try:
            if schedule_type == 'immediate':
                self._execute_campaign_async(campaign_id)
            
            elif schedule_type == 'delayed':
                if schedule_time:
                    schedule.every().day.at(schedule_time).do(
                        self._execute_campaign, campaign_id
                    ).tag(campaign_id)
                    logger.info(f"Scheduled campaign {campaign_id} for {schedule_time}")
            
            elif schedule_type == 'daily':
                schedule.every().day.at(schedule_time or "09:00").do(
                    self._execute_campaign, campaign_id
                ).tag(campaign_id)
                logger.info(f"Scheduled daily campaign {campaign_id}")
            
            elif schedule_type == 'weekly':
                schedule.every().week.do(
                    self._execute_campaign, campaign_id
                ).tag(campaign_id)
                logger.info(f"Scheduled weekly campaign {campaign_id}")
            
            elif schedule_type == 'monthly':
                schedule.every(30).days.do(
                    self._execute_campaign, campaign_id
                ).tag(campaign_id)
                logger.info(f"Scheduled monthly campaign {campaign_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling campaign {campaign_id}: {str(e)}")
    
    def cancel_scheduled_campaign(self, campaign_id):
        """Cancel scheduled campaign"""
        try:
            schedule.clear(campaign_id)
            logger.info(f"Cancelled scheduled campaign {campaign_id}")
        except Exception as e:
            logger.error(f"Error cancelling campaign {campaign_id}: {str(e)}")
    
    def _execute_campaign_async(self, campaign_id):
        """Execute campaign in a separate thread"""
        def run_campaign():
            self._execute_campaign(campaign_id)
        
        campaign_thread = threading.Thread(target=run_campaign, daemon=True)
        campaign_thread.start()
    
    def _execute_campaign(self, campaign_id):
        """Execute a ping campaign"""
        try:
            logger.info(f"Executing scheduled campaign: {campaign_id}")
            
            campaign = self.url_manager.get_campaign(campaign_id)
            if not campaign:
                logger.error(f"Campaign {campaign_id} not found")
                return
            
            # Update status to processing
            self.url_manager.update_campaign_status(campaign_id, 'processing')
            
            # Execute comprehensive ping
            urls = campaign['urls']
            results = self.ping_services.comprehensive_ping(urls, campaign_id)
            
            # Update campaign with results
            self.url_manager.update_campaign_status(campaign_id, 'completed', results)
            
            logger.info(f"Completed scheduled campaign: {campaign_id}")
            
        except Exception as e:
            logger.error(f"Error executing campaign {campaign_id}: {str(e)}")
            self.url_manager.update_campaign_status(campaign_id, 'failed')
    
    def get_scheduled_jobs(self):
        """Get list of scheduled jobs"""
        jobs = []
        for job in schedule.jobs:
            jobs.append({
                'tags': list(job.tags),
                'next_run': job.next_run.isoformat() if job.next_run else None,
                'interval': str(job.interval),
                'unit': job.unit
            })
        return jobs
    
    def schedule_retry_failed_pings(self, campaign_id, retry_delay_hours=1):
        """Schedule retry for failed pings"""
        try:
            retry_time = datetime.now() + timedelta(hours=retry_delay_hours)
            schedule.every().day.at(retry_time.strftime("%H:%M")).do(
                self._retry_failed_pings, campaign_id
            ).tag(f"retry_{campaign_id}")
            
            logger.info(f"Scheduled retry for campaign {campaign_id} at {retry_time}")
            
        except Exception as e:
            logger.error(f"Error scheduling retry for campaign {campaign_id}: {str(e)}")
    
    def _retry_failed_pings(self, campaign_id):
        """Retry failed pings for a campaign"""
        try:
            logger.info(f"Retrying failed pings for campaign: {campaign_id}")
            
            campaign = self.url_manager.get_campaign(campaign_id)
            if not campaign:
                logger.error(f"Campaign {campaign_id} not found for retry")
                return
            
            # Get failed ping services from previous results
            results = campaign.get('results', {})
            failed_services = []
            
            # Identify failed services (this is simplified - in practice you'd want more sophisticated logic)
            for feed_type, rss_results in results.get('rss_pings', {}).items():
                for service, result in rss_results.items():
                    if not result.get('success'):
                        failed_services.append(('rss', service))
            
            if failed_services:
                # Re-execute pings for failed services only
                retry_results = self.ping_services.comprehensive_ping(campaign['urls'], campaign_id)
                
                # Merge retry results with original results
                self._merge_retry_results(campaign_id, retry_results)
                
                logger.info(f"Completed retry for campaign: {campaign_id}")
            else:
                logger.info(f"No failed services to retry for campaign: {campaign_id}")
            
        except Exception as e:
            logger.error(f"Error retrying failed pings for campaign {campaign_id}: {str(e)}")
    
    def _merge_retry_results(self, campaign_id, retry_results):
        """Merge retry results with original campaign results"""
        try:
            campaign = self.url_manager.get_campaign(campaign_id)
            if campaign:
                original_results = campaign.get('results', {})
                
                # Simple merge - in practice you'd want more sophisticated merging logic
                merged_results = {**original_results, **retry_results}
                
                self.url_manager.update_campaign_status(campaign_id, 'completed', merged_results)
                
        except Exception as e:
            logger.error(f"Error merging retry results for campaign {campaign_id}: {str(e)}")
