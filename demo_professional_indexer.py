#!/usr/bin/env python3
"""
Professional Indexer Demo - Alternative to Tor Browser for SEO Indexing

This demonstrates how to use the professional indexing system instead of Tor,
providing better performance, reliability, and compliance while achieving
the same goals of avoiding detection during bulk backlink indexing.
"""

import logging
from modules.professional_indexer import ProfessionalIndexer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demo_standard_rotation():
    """Demo without proxy services (User-Agent rotation only)"""
    logger.info("🚀 Starting Professional Indexer Demo - Standard Rotation")
    
    # Test URLs
    test_urls = [
        "https://example.com/page1",
        "https://example.com/page2", 
        "https://example.com/page3",
        "https://httpbin.org/status/200",
        "https://httpbin.org/user-agent"
    ]
    
    # Initialize professional indexer without proxy rotation
    indexer = ProfessionalIndexer(
        enable_proxy_rotation=False,
        rotation_interval=5
    )
    
    try:
        # Setup the system
        setup_success = indexer.setup_professional_rotation()
        if not setup_success:
            logger.error("❌ Failed to setup professional indexing")
            return
        
        logger.info("✅ Professional indexing system initialized")
        
        # Execute professional campaign
        results = indexer.professional_ping_campaign(
            urls=test_urls,
            campaign_name="Demo Campaign - Standard Rotation",
            categories=["google", "global_rss"],  # Target specific categories
            include_advanced=True
        )
        
        # Display results
        print("\n" + "="*60)
        print("📊 PROFESSIONAL INDEXING RESULTS")
        print("="*60)
        
        print(f"Campaign: {results['campaign_name']}")
        print(f"URLs Processed: {results['urls_count']}")
        print(f"Timestamp: {results['timestamp']}")
        
        # Configuration details
        config = results['configuration']
        print(f"\n🔧 Configuration:")
        print(f"  Proxy Rotation: {config['proxy_rotation']}")
        print(f"  Rotation Interval: {config['rotation_interval']}")
        print(f"  Categories: {config['categories']}")
        print(f"  Advanced Methods: {config['advanced_methods']}")
        
        # Performance metrics
        if 'metrics' in results:
            metrics = results['metrics']
            print(f"\n📈 Performance Metrics:")
            print(f"  Overall Success Rate: {metrics['overall_success_rate']:.1f}%")
            print(f"  Traditional Success Rate: {metrics['traditional_success_rate']:.1f}%")
            print(f"  Advanced Success Rate: {metrics['advanced_success_rate']:.1f}%")
            print(f"  Total Services Contacted: {metrics['total_services_contacted']}")
            print(f"  Unique Methods Used: {', '.join(metrics['unique_methods_used'])}")
            print(f"  Session Duration: {metrics['session_duration']:.1f} seconds")
            print(f"  Requests Per Minute: {metrics['requests_per_minute']:.1f}")
        
        # Advanced methods results
        if 'advanced_methods' in results['results']:
            advanced = results['results']['advanced_methods']
            if 'enhanced_crawling' in advanced:
                crawling = advanced['enhanced_crawling']
                print(f"\n🕸️ Enhanced Crawling:")
                print(f"  Total Crawls: {crawling.get('total_crawls', 0)}")
                print(f"  Successful Crawls: {crawling.get('successful_crawls', 0)}")
                print(f"  Unique IPs Used: {crawling.get('unique_ips_count', 0)}")
                print(f"  Proxy Rotation: {crawling.get('proxy_rotation_enabled', False)}")
        
        # Session summary
        session_summary = indexer.get_session_summary()
        print(f"\n📋 Session Summary:")
        stats = session_summary['session_stats']
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Successful Pings: {stats['successful_pings']}")
        print(f"  Failed Pings: {stats['failed_pings']}")
        print(f"  IP Rotations: {stats['ip_rotations']}")
        
        capabilities = session_summary['capabilities']
        print(f"  Available RSS Services: {capabilities['total_rss_services']}")
        print(f"  Available Search Engines: {capabilities['total_search_engines']}")
        print(f"  Advanced Methods: {', '.join(capabilities['advanced_methods'])}")
        
        logger.info("✅ Demo completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
        return None

def demo_proxy_rotation():
    """Demo with proxy services (requires configuration)"""
    logger.info("🔄 Starting Professional Indexer Demo - Proxy Rotation")
    
    test_urls = [
        "https://httpbin.org/ip",
        "https://httpbin.org/user-agent", 
        "https://httpbin.org/headers"
    ]
    
    # Initialize with proxy rotation enabled
    indexer = ProfessionalIndexer(
        enable_proxy_rotation=True,
        rotation_interval=3  # Rotate more frequently for demo
    )
    
    try:
        setup_success = indexer.setup_professional_rotation()
        
        if not setup_success:
            print("⚠️ Proxy rotation not configured")
            print("To enable proxy rotation, set environment variables:")
            print("  PROXY_HTTP=http://username:password@proxy-server:port")
            print("  PROXY_HTTPS=https://username:password@proxy-server:port")
            print("\nContinuing with enhanced User-Agent rotation...")
        
        # Execute campaign with proxy support
        results = indexer.professional_ping_campaign(
            urls=test_urls,
            campaign_name="Demo Campaign - Proxy Rotation",
            categories=["google", "global_rss"],
            include_advanced=True
        )
        
        print("\n" + "="*60)
        print("🔄 PROXY ROTATION DEMO RESULTS")  
        print("="*60)
        
        # Show proxy configuration status
        session = indexer.get_session_summary()
        config = session['configuration']
        print(f"Proxy Configured: {config['proxy_configured']}")
        print(f"Proxy Rotation Enabled: {config['proxy_rotation_enabled']}")
        
        # Show rotation effectiveness
        if 'advanced_methods' in results['results']:
            advanced = results['results']['advanced_methods']
            if 'enhanced_crawling' in advanced:
                crawling = advanced['enhanced_crawling']
                ip_count = crawling.get('unique_ips_count', 0)
                print(f"Unique IP Addresses Used: {ip_count}")
                
                if crawling.get('ip_addresses_used'):
                    print("IP Addresses:")
                    for i, ip in enumerate(crawling['ip_addresses_used'][:5]):
                        print(f"  {i+1}. {ip}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Proxy demo failed: {str(e)}")
        return None

def compare_with_tor_approach():
    """Compare professional approach with Tor requirements"""
    print("\n" + "="*80)
    print("🔍 PROFESSIONAL INDEXER VS TOR COMPARISON")
    print("="*80)
    
    comparison = {
        'Professional Indexer': {
            'IP Rotation': '✅ Via legitimate proxy services',
            'Speed': '✅ Fast (no multi-hop routing)',
            'Reliability': '✅ High success rates',
            'Platform Compliance': '✅ Replit-approved',
            'Setup Complexity': '✅ Simple configuration',
            'Detection Avoidance': '✅ User-Agent + proxy rotation',
            'Cost': '✅ Optional proxy services only',
            'Maintenance': '✅ Self-managing',
            'Performance': '✅ Optimized for SEO indexing'
        },
        'Tor Browser Approach': {
            'IP Rotation': '❌ Against Replit policies',
            'Speed': '❌ Slow (multiple hops)',
            'Reliability': '❌ Connection issues',
            'Platform Compliance': '❌ Policy violations',
            'Setup Complexity': '❌ Complex installation',
            'Detection Avoidance': '⚠️ Often blocked by services',
            'Cost': '✅ Free but risky',
            'Maintenance': '❌ Frequent issues',
            'Performance': '❌ Not optimized for bulk operations'
        }
    }
    
    for approach, features in comparison.items():
        print(f"\n{approach}:")
        for feature, status in features.items():
            print(f"  {feature}: {status}")
    
    print(f"\n🎯 RECOMMENDATION:")
    print(f"Use Professional Indexer for:")
    print(f"  • Legitimate SEO indexing campaigns")
    print(f"  • High-volume backlink processing") 
    print(f"  • Professional grade reliability")
    print(f"  • Replit platform compliance")

def main():
    """Main demo function"""
    print("🚀 FREE PING INDEXER PRO - PROFESSIONAL ROTATION DEMO")
    print("Alternative to Tor Browser for SEO Indexing")
    print("="*60)
    
    # Demo 1: Standard rotation
    print("\n1️⃣ DEMO: Standard Professional Rotation")
    standard_results = demo_standard_rotation()
    
    # Demo 2: Proxy rotation (if configured)
    print("\n2️⃣ DEMO: Enhanced Proxy Rotation")
    proxy_results = demo_proxy_rotation()
    
    # Demo 3: Comparison
    print("\n3️⃣ COMPARISON: Professional vs Tor")
    compare_with_tor_approach()
    
    # Final summary
    print("\n" + "="*60)
    print("✅ DEMO COMPLETE")
    print("="*60)
    print("Your Free Ping Indexer Pro now includes:")
    print("• Professional proxy rotation system")
    print("• 90+ ping services with smart categorization")  
    print("• Advanced indexing methods")
    print("• Enhanced User-Agent rotation")
    print("• Comprehensive success tracking")
    print("\nThis provides all the benefits of IP rotation")
    print("without the risks and limitations of Tor.")

if __name__ == "__main__":
    main()