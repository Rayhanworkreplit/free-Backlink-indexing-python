import os
import json
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from app import app
from modules.url_manager import URLManager
from modules.ping_services import PingServices
from modules.enhanced_ping_services import EnhancedPingServices
from modules.live_progress import live_progress_tracker
from modules.reporting import ReportingManager
from modules.success_booster import SuccessRateBooster
from modules.modern_services import ModernPingServices
from modules.rss_generator import RSSGenerator
from modules.sitemap_manager import SitemapManager
from modules.archive_tools import ArchiveTools
from utils.schedulers import PingScheduler
from utils.file_manager import FileManager
from utils.validators import URLValidator
import logging
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize managers
url_manager = URLManager()
ping_services = PingServices()
enhanced_ping_services = EnhancedPingServices()
reporting_manager = ReportingManager()
ping_scheduler = PingScheduler()
file_manager = FileManager()
url_validator = URLValidator()
success_booster = SuccessRateBooster()
modern_services = ModernPingServices()

# Store campaign progress data
campaign_progress = {}

# Start the scheduler
ping_scheduler.start_scheduler()

@app.route('/')
def index():
    """Main dashboard"""
    try:
        # Get analytics data
        analytics = reporting_manager.generate_analytics_data()
        
        # Get ping services info
        ping_services_info = {
            'rss_services': ping_services.rss_services,
            'search_engines': ping_services.search_engines,
            'directories': ping_services.directories
        }
        
        return render_template('index.html', 
                             stats=analytics.get('overview', {}),
                             recent_campaigns=analytics.get('recent_campaigns', []),
                             ping_services=ping_services_info)
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        flash(f"Error loading dashboard: {str(e)}", 'error')
        return render_template('index.html', 
                             stats={}, recent_campaigns=[], ping_services={})

@app.route('/bulk-upload')
def bulk_upload():
    """Bulk URL upload page"""
    try:
        # Get service counts for display
        service_counts = {
            'rss_services_count': len(ping_services.rss_services),
            'search_engines_count': len(ping_services.search_engines),
            'directories_count': len(ping_services.directories),
            'max_urls': 10000  # From config
        }
        
        return render_template('bulk_upload.html', **service_counts)
    except Exception as e:
        logger.error(f"Error loading bulk upload page: {str(e)}")
        flash(f"Error loading page: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/create-campaign', methods=['POST'])
def create_campaign():
    """Create new ping campaign"""
    try:
        input_type = request.form.get('input_type')
        ping_methods = request.form.getlist('ping_methods')
        schedule_type = request.form.get('schedule_type', 'immediate')
        schedule_time = request.form.get('schedule_time')
        
        # Get URLs based on input type
        urls = []
        campaign_name = ""
        
        if input_type == 'text':
            campaign_name = request.form.get('campaign_name', 'Text Campaign')
            urls_text = request.form.get('urls_text', '')
            urls = url_manager.parse_bulk_urls(urls_text, 'text')
        elif input_type == 'csv':
            campaign_name = request.form.get('campaign_name_csv', 'CSV Campaign')
            csv_data = request.form.get('csv_data', '')
            urls = url_manager.parse_bulk_urls(csv_data, 'csv')
        elif input_type == 'manual':
            campaign_name = request.form.get('campaign_name_manual', 'Manual Campaign')
            manual_urls = request.form.getlist('manual_urls')
            urls = [url.strip() for url in manual_urls if url.strip()]
        
        if not urls:
            flash('No valid URLs provided', 'error')
            return redirect(url_for('bulk_upload'))
        
        if not ping_methods:
            flash('Please select at least one ping method', 'error')
            return redirect(url_for('bulk_upload'))
        
        # Create campaign
        campaign_id, campaign = url_manager.create_campaign(
            name=campaign_name,
            urls=urls,
            ping_methods=ping_methods
        )
        
        # Schedule the campaign
        ping_scheduler.schedule_campaign(campaign_id, schedule_type, schedule_time)
        
        flash(f'Campaign "{campaign_name}" created successfully with {len(urls)} URLs!', 'success')
        return redirect(url_for('view_campaign', campaign_id=campaign_id))
        
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        flash(f"Error creating campaign: {str(e)}", 'error')
        return redirect(url_for('bulk_upload'))

@app.route('/campaigns')
def campaigns():
    """List all campaigns"""
    try:
        campaigns = url_manager.load_campaigns()
        
        # Convert to list and add calculated fields
        campaigns_list = []
        for campaign_id, campaign in campaigns.items():
            campaign_data = {
                'id': campaign_id,
                'name': campaign.get('name', 'Unnamed Campaign'),
                'status': campaign.get('status', 'unknown'),
                'created_date': campaign.get('created_date', ''),
                'total_urls': campaign.get('total_urls', 0),
                'successful_pings': campaign.get('successful_pings', 0),
                'failed_pings': campaign.get('failed_pings', 0),
                'ping_methods': campaign.get('ping_methods', [])
            }
            
            # Calculate success rate
            total_pings = campaign_data['successful_pings'] + campaign_data['failed_pings']
            if total_pings > 0:
                campaign_data['success_rate'] = round(
                    (campaign_data['successful_pings'] / total_pings) * 100, 2
                )
            else:
                campaign_data['success_rate'] = 0
            
            campaigns_list.append(campaign_data)
        
        # Sort by creation date (most recent first)
        campaigns_list.sort(key=lambda x: x['created_date'], reverse=True)
        
        return render_template('campaign.html', campaigns=campaigns_list)
        
    except Exception as e:
        logger.error(f"Error loading campaigns: {str(e)}")
        flash(f"Error loading campaigns: {str(e)}", 'error')
        return render_template('campaign.html', campaigns=[])

@app.route('/campaign/<campaign_id>')
def view_campaign(campaign_id):
    """View specific campaign details"""
    try:
        campaign = url_manager.get_campaign(campaign_id)
        if not campaign:
            flash('Campaign not found', 'error')
            return redirect(url_for('campaigns'))
        
        # Calculate additional statistics
        results = campaign.get('results', {})
        
        # Count service-specific results
        service_stats = {
            'rss_total': 0,
            'rss_success': 0,
            'sitemap_total': 0,
            'sitemap_success': 0,
            'archive_total': 0,
            'archive_success': 0,
            'directory_total': 0,
            'directory_success': 0
        }
        
        # RSS stats
        for feed_type, rss_results in results.get('rss_pings', {}).items():
            for service, result in rss_results.items():
                service_stats['rss_total'] += 1
                if result.get('success'):
                    service_stats['rss_success'] += 1
        
        # Sitemap stats
        for engine, result in results.get('sitemap_pings', {}).items():
            service_stats['sitemap_total'] += 1
            if result.get('success'):
                service_stats['sitemap_success'] += 1
        
        # Archive stats
        for url, result in results.get('archive_saves', {}).items():
            service_stats['archive_total'] += 1
            if result.get('success'):
                service_stats['archive_success'] += 1
        
        # Directory stats
        for url, dir_results in results.get('directory_submissions', {}).items():
            for directory, result in dir_results.items():
                service_stats['directory_total'] += 1
                if result.get('success'):
                    service_stats['directory_success'] += 1
        
        return render_template('campaign_detail.html', 
                             campaign=campaign, 
                             campaign_id=campaign_id,
                             service_stats=service_stats)
        
    except Exception as e:
        logger.error(f"Error viewing campaign {campaign_id}: {str(e)}")
        flash(f"Error loading campaign: {str(e)}", 'error')
        return redirect(url_for('campaigns'))

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    try:
        analytics_data = reporting_manager.generate_analytics_data()
        return render_template('analytics.html', analytics=analytics_data)
    except Exception as e:
        logger.error(f"Error loading analytics: {str(e)}")
        flash(f"Error loading analytics: {str(e)}", 'error')
        return render_template('analytics.html', analytics={})

@app.route('/quick-ping', methods=['POST'])
def quick_ping():
    """Quick ping single URL"""
    try:
        url = request.form.get('url', '').strip()
        methods = request.form.getlist('methods')
        
        if not url:
            flash('Please provide a URL', 'error')
            return redirect(url_for('index'))
        
        if not url_validator.is_valid_url(url):
            flash('Invalid URL format', 'error')
            return redirect(url_for('index'))
        
        # Create a quick campaign
        campaign_id, campaign = url_manager.create_campaign(
            name=f"Quick Ping - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            urls=[url],
            ping_methods=methods
        )
        
        # Execute immediately in background
        def execute_quick_ping():
            results = ping_services.comprehensive_ping([url], campaign_id)
            url_manager.update_campaign_status(campaign_id, 'completed', results)
        
        ping_thread = threading.Thread(target=execute_quick_ping, daemon=True)
        ping_thread.start()
        
        flash(f'Quick ping started for {url}', 'success')
        return redirect(url_for('view_campaign', campaign_id=campaign_id))
        
    except Exception as e:
        logger.error(f"Error with quick ping: {str(e)}")
        flash(f"Error with quick ping: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/webhooks')
def webhooks():
    """Webhook management page"""
    try:
        # Get webhook status from ping services
        webhook_status = ping_services.webhook_manager.get_webhook_status()
        return render_template('webhooks.html', webhook_status=webhook_status)
    except Exception as e:
        logger.error(f"Error loading webhooks page: {str(e)}")
        flash(f"Error loading webhooks page: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/test-webhook', methods=['POST'])
def test_webhook():
    """Test webhook connection"""
    try:
        result = ping_services.webhook_manager.test_webhook_connection('hashnode')
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error testing webhook: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/export-data')
def export_data():
    """Export data page"""
    try:
        campaigns = url_manager.load_campaigns()
        file_stats = file_manager.get_file_stats()
        
        return render_template('export_data.html', 
                             campaigns=campaigns, 
                             file_stats=file_stats)
    except Exception as e:
        logger.error(f"Error loading export page: {str(e)}")
        flash(f"Error loading export page: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/export-campaign/<campaign_id>/<format>')
def export_campaign(campaign_id, format):
    """Export specific campaign data"""
    try:
        if format not in ['csv', 'json']:
            flash('Invalid export format', 'error')
            return redirect(url_for('campaigns'))
        
        data = url_manager.export_results(campaign_id, format)
        
        if format == 'csv':
            response = make_response(data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=campaign_{campaign_id}.csv'
        else:  # json
            response = make_response(data)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename=campaign_{campaign_id}.json'
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting campaign {campaign_id}: {str(e)}")
        flash(f"Error exporting campaign: {str(e)}", 'error')
        return redirect(url_for('campaigns'))

@app.route('/system-status')
def system_status():
    """System status page"""
    try:
        file_stats = file_manager.get_file_stats()
        disk_usage = file_manager.get_disk_usage()
        scheduled_jobs = ping_scheduler.get_scheduled_jobs()
        
        system_info = {
            'file_stats': file_stats,
            'disk_usage': disk_usage,
            'scheduled_jobs': scheduled_jobs,
            'service_counts': {
                'rss_services': len(ping_services.rss_services),
                'search_engines': len(ping_services.search_engines),
                'directories': len(ping_services.directories)
            }
        }
        
        return render_template('system_status.html', system_info=system_info)
        
    except Exception as e:
        logger.error(f"Error loading system status: {str(e)}")
        flash(f"Error loading system status: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/delete-campaign/<campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    """Delete a campaign"""
    try:
        campaigns = url_manager.load_campaigns()
        if campaign_id in campaigns:
            del campaigns[campaign_id]
            url_manager.save_campaigns(campaigns)
            
            # Cancel any scheduled jobs
            ping_scheduler.cancel_scheduled_campaign(campaign_id)
            
            flash('Campaign deleted successfully', 'success')
        else:
            flash('Campaign not found', 'error')
            
    except Exception as e:
        logger.error(f"Error deleting campaign {campaign_id}: {str(e)}")
        flash(f"Error deleting campaign: {str(e)}", 'error')
    
    return redirect(url_for('campaigns'))

@app.route('/retry-campaign/<campaign_id>', methods=['POST'])
def retry_campaign(campaign_id):
    """Retry failed pings for a campaign"""
    try:
        campaign = url_manager.get_campaign(campaign_id)
        if not campaign:
            flash('Campaign not found', 'error')
            return redirect(url_for('campaigns'))
        
        # Schedule retry
        ping_scheduler.schedule_retry_failed_pings(campaign_id)
        
        flash('Campaign retry scheduled', 'success')
        return redirect(url_for('view_campaign', campaign_id=campaign_id))
        
    except Exception as e:
        logger.error(f"Error retrying campaign {campaign_id}: {str(e)}")
        flash(f"Error retrying campaign: {str(e)}", 'error')
        return redirect(url_for('campaigns'))

# Serve generated RSS feeds and sitemaps
@app.route('/feeds/<feed_type>/<campaign_id>')
def serve_rss_feed(feed_type, campaign_id):
    """Serve generated RSS feeds"""
    try:
        # This is a placeholder - in practice you'd serve the actual file
        # For now, generate on-demand
        campaign = url_manager.get_campaign(campaign_id)
        if not campaign:
            return "Feed not found", 404
        
        rss_gen = RSSGenerator()
        filepath, xml_content = rss_gen.generate_rss_feed(
            campaign['urls'], feed_type, campaign_id
        )
        
        response = make_response(xml_content)
        response.headers['Content-Type'] = 'application/rss+xml'
        return response
        
    except Exception as e:
        logger.error(f"Error serving RSS feed: {str(e)}")
        return "Error generating feed", 500

@app.route('/sitemaps/<filename>')
def serve_sitemap(filename):
    """Serve generated sitemaps"""
    try:
        sitemap_path = os.path.join('data/sitemaps', filename)
        if os.path.exists(sitemap_path):
            with open(sitemap_path, 'r') as f:
                xml_content = f.read()
            
            response = make_response(xml_content)
            response.headers['Content-Type'] = 'application/xml'
            return response
        else:
            return "Sitemap not found", 404
            
    except Exception as e:
        logger.error(f"Error serving sitemap: {str(e)}")
        return "Error serving sitemap", 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/success_boost')
def success_boost():
    """Enhanced success rate ping interface"""
    try:
        recommendations = modern_services.get_service_recommendations()
        verified_services = success_booster.get_verified_services()
        
        return render_template('success_boost.html', 
                             recommendations=recommendations,
                             verified_services=verified_services,
                             service_count=len(verified_services))
    except Exception as e:
        logger.error(f"Error loading success boost page: {str(e)}")
        return render_template('success_boost.html', error=str(e))

@app.route('/execute_boost', methods=['POST'])
def execute_boost():
    """Execute enhanced success rate campaign"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        enable_proxy = data.get('enable_proxy', False)
        use_modern_only = data.get('use_modern_only', True)
        
        if not urls:
            return jsonify({'error': 'No URLs provided'}), 400
        
        # Validate URLs
        valid_urls = []
        for url in urls:
            if url_validator.is_valid(url):
                valid_urls.append(url)
        
        if not valid_urls:
            return jsonify({'error': 'No valid URLs provided'}), 400
        
        logger.info(f"Executing success boost for {len(valid_urls)} URLs")
        
        if use_modern_only:
            # Use modern high-success services
            result = modern_services.bulk_modern_ping(valid_urls, min_success_rate=85)
        else:
            # Use comprehensive boosting strategy
            result = success_booster.comprehensive_success_boost(valid_urls, enable_proxy)
        
        # Log results for monitoring
        logger.info(f"Success boost completed: {result.get('success_rate', 0):.1f}% success rate")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error executing success boost: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/demo_boost')
def demo_boost():
    """Demo page showing success rate improvements"""
    try:
        # Get sample data for demo
        demo_data = {
            'before': {
                'success_rate': 45.2,
                'total_services': 90,
                'working_services': 41,
                'major_issues': [
                    'Many HTTP services not working (SSL required)',
                    'Outdated endpoints returning 404',
                    'DNS resolution failures',
                    'SSL certificate verification errors'
                ]
            },
            'after': {
                'success_rate': 87.4,
                'total_services': 25,
                'working_services': 22,
                'improvements': [
                    'Verified modern HTTPS endpoints only',
                    'Google/Bing direct API integration',
                    'Professional proxy rotation',
                    'Intelligent retry with alternatives',
                    'Real-time service health monitoring'
                ]
            },
            'boost_features': {
                'modern_services': len(modern_services.get_optimized_service_list(80)),
                'verified_endpoints': len(success_booster.get_verified_services()),
                'success_improvement': 87.4 - 45.2,
                'efficiency_gain': '3x faster with fewer but working services'
            }
        }
        
        return render_template('demo_boost.html', demo_data=demo_data)
        
    except Exception as e:
        logger.error(f"Error loading demo: {str(e)}")
        return render_template('demo_boost.html', demo_data={}, error=str(e))

# API Endpoints for Live Progress Tracking

@app.route('/api/campaign-progress/<campaign_id>')
def get_campaign_progress(campaign_id):
    """Get real-time progress for a campaign"""
    try:
        progress_data = live_progress_tracker.get_campaign_progress(campaign_id)
        if progress_data:
            return jsonify(progress_data)
        else:
            return jsonify({'error': 'Campaign not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching progress for campaign {campaign_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/active-campaigns')
def get_active_campaigns():
    """Get list of all active campaigns"""
    try:
        campaigns = live_progress_tracker.get_all_active_campaigns()
        return jsonify(campaigns)
    except Exception as e:
        logger.error(f"Error fetching active campaigns: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/start-live-campaign', methods=['POST'])
def start_live_campaign():
    """Start a campaign with live progress tracking"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        categories = data.get('categories', ['google_services', 'modern_ping_services', 'seo_tools'])
        
        if not urls:
            return jsonify({'error': 'No URLs provided'}), 400
        
        # Validate URLs
        valid_urls = [url for url in urls if url_validator.is_valid(url)]
        if not valid_urls:
            return jsonify({'error': 'No valid URLs provided'}), 400
        
        # Get services for selected categories
        services = enhanced_ping_services.get_services_by_category(categories)
        total_pings = len(valid_urls) * len(services)
        
        # Generate campaign ID
        import time
        campaign_id = f"live_{int(time.time())}"
        
        # Start progress tracking
        live_progress_tracker.start_campaign(campaign_id, len(services), len(valid_urls))
        
        # Execute pings in background with progress updates
        def execute_with_progress():
            try:
                for url in valid_urls:
                    for service in services:
                        # Get service category for appropriate timeout
                        category = enhanced_ping_services._get_service_category(service)
                        
                        # Execute actual ping
                        result = enhanced_ping_services._ping_single_service(url, service, category)
                        
                        if result:
                            success = result.get('success', False)
                            response_time = result.get('response_time', 0)
                            
                            # Update progress
                            live_progress_tracker.update_progress(campaign_id, service, url, success, response_time)
                
                # Mark as complete
                live_progress_tracker.complete_campaign(campaign_id)
                
            except Exception as e:
                logger.error(f"Error in live campaign execution: {str(e)}")
        
        # Start background execution
        thread = threading.Thread(target=execute_with_progress)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'total_services': len(services),
            'total_urls': len(valid_urls),
            'total_pings': total_pings,
            'message': f'Started live campaign with {len(valid_urls)} URLs and {len(services)} services'
        })
        
    except Exception as e:
        logger.error(f"Error starting live campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/service-categories')
def get_service_categories():
    """Get available service categories"""
    try:
        categories = enhanced_ping_services.get_service_categories()
        stats = enhanced_ping_services.get_service_stats()
        
        return jsonify({
            'categories': categories,
            'stats': stats,
            'total_services': sum(stats.values()) if isinstance(stats, dict) else 0
        })
        
    except Exception as e:
        logger.error(f"Error fetching service categories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/live-progress')
def live_progress():
    """Live progress demo page"""
    try:
        return render_template('live_progress.html')
    except Exception as e:
        logger.error(f"Error loading live progress page: {str(e)}")
        flash(f"Error loading page: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/simple-progress-test')
def simple_progress_test():
    """Simple progress test page"""
    try:
        return render_template('simple_progress_test.html')
    except Exception as e:
        logger.error(f"Error loading simple progress test page: {str(e)}")
        flash(f"Error loading page: {str(e)}", 'error')
        return redirect(url_for('index'))
