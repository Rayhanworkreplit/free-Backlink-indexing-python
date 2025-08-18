import os
import json
import shutil
import logging
from datetime import datetime, timedelta
from config import Config

logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self):
        self.config = Config()
    
    def cleanup_old_files(self, days_old=30):
        """Clean up old RSS feeds and sitemaps"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Clean RSS feeds
            rss_count = self._cleanup_directory(self.config.RSS_FEEDS_DIR, cutoff_date)
            
            # Clean sitemaps
            sitemap_count = self._cleanup_directory(self.config.SITEMAPS_DIR, cutoff_date)
            
            logger.info(f"Cleaned up {rss_count} RSS feeds and {sitemap_count} sitemaps older than {days_old} days")
            
            return {
                'rss_files_cleaned': rss_count,
                'sitemap_files_cleaned': sitemap_count,
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during file cleanup: {str(e)}")
            return {'error': str(e)}
    
    def _cleanup_directory(self, directory, cutoff_date):
        """Clean up files in a specific directory"""
        cleaned_count = 0
        
        try:
            if not os.path.exists(directory):
                return cleaned_count
            
            for filename in os.listdir(directory):
                if filename.startswith('.'):  # Skip hidden files
                    continue
                
                filepath = os.path.join(directory, filename)
                
                if os.path.isfile(filepath):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if file_mtime < cutoff_date:
                        os.remove(filepath)
                        cleaned_count += 1
                        logger.debug(f"Removed old file: {filepath}")
            
        except Exception as e:
            logger.error(f"Error cleaning directory {directory}: {str(e)}")
        
        return cleaned_count
    
    def get_file_stats(self):
        """Get statistics about stored files"""
        try:
            stats = {
                'rss_feeds': self._get_directory_stats(self.config.RSS_FEEDS_DIR),
                'sitemaps': self._get_directory_stats(self.config.SITEMAPS_DIR),
                'data_files': self._get_data_file_stats()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting file stats: {str(e)}")
            return {}
    
    def _get_directory_stats(self, directory):
        """Get statistics for a directory"""
        stats = {
            'file_count': 0,
            'total_size_bytes': 0,
            'total_size_mb': 0,
            'oldest_file': None,
            'newest_file': None
        }
        
        try:
            if not os.path.exists(directory):
                return stats
            
            oldest_time = None
            newest_time = None
            
            for filename in os.listdir(directory):
                if filename.startswith('.'):  # Skip hidden files
                    continue
                
                filepath = os.path.join(directory, filename)
                
                if os.path.isfile(filepath):
                    stats['file_count'] += 1
                    
                    # File size
                    file_size = os.path.getsize(filepath)
                    stats['total_size_bytes'] += file_size
                    
                    # File times
                    file_mtime = os.path.getmtime(filepath)
                    file_datetime = datetime.fromtimestamp(file_mtime)
                    
                    if oldest_time is None or file_mtime < oldest_time:
                        oldest_time = file_mtime
                        stats['oldest_file'] = {
                            'name': filename,
                            'date': file_datetime.isoformat(),
                            'size_bytes': file_size
                        }
                    
                    if newest_time is None or file_mtime > newest_time:
                        newest_time = file_mtime
                        stats['newest_file'] = {
                            'name': filename,
                            'date': file_datetime.isoformat(),
                            'size_bytes': file_size
                        }
            
            stats['total_size_mb'] = round(stats['total_size_bytes'] / (1024 * 1024), 2)
            
        except Exception as e:
            logger.error(f"Error getting directory stats for {directory}: {str(e)}")
        
        return stats
    
    def _get_data_file_stats(self):
        """Get statistics for data files"""
        stats = {}
        
        data_files = ['campaigns.json', 'ping_results.json']
        
        for filename in data_files:
            filepath = os.path.join(self.config.DATA_DIR, filename)
            
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                stats[filename] = {
                    'exists': True,
                    'size_bytes': file_size,
                    'size_kb': round(file_size / 1024, 2),
                    'last_modified': file_mtime.isoformat()
                }
            else:
                stats[filename] = {'exists': False}
        
        return stats
    
    def backup_data_files(self):
        """Create backup of important data files"""
        try:
            backup_dir = os.path.join(self.config.DATA_DIR, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            backup_files = []
            data_files = ['campaigns.json', 'ping_results.json']
            
            for filename in data_files:
                source_path = os.path.join(self.config.DATA_DIR, filename)
                
                if os.path.exists(source_path):
                    backup_filename = f"{filename}_{timestamp}.backup"
                    backup_path = os.path.join(backup_dir, backup_filename)
                    
                    shutil.copy2(source_path, backup_path)
                    backup_files.append(backup_filename)
                    logger.info(f"Backed up {filename} to {backup_filename}")
            
            return {
                'success': True,
                'backup_files': backup_files,
                'backup_directory': backup_dir,
                'timestamp': timestamp
            }
            
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def export_campaign_data(self, campaign_id, export_format='json'):
        """Export specific campaign data"""
        try:
            from modules.url_manager import URLManager
            url_manager = URLManager()
            
            campaign = url_manager.get_campaign(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            if export_format == 'json':
                return json.dumps(campaign, indent=2)
            elif export_format == 'csv':
                return url_manager.export_results(campaign_id, 'csv')
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
                
        except Exception as e:
            logger.error(f"Error exporting campaign data: {str(e)}")
            raise
    
    def get_disk_usage(self):
        """Get disk usage information for the application"""
        try:
            total_size = 0
            
            # Calculate size of all application directories
            for root, dirs, files in os.walk('.'):
                for file in files:
                    filepath = os.path.join(root, file)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            
            return {
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_size_gb': round(total_size / (1024 * 1024 * 1024), 3)
            }
            
        except Exception as e:
            logger.error(f"Error calculating disk usage: {str(e)}")
            return {'error': str(e)}
