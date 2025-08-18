import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    
    # Ping service timeouts
    RSS_PING_TIMEOUT = 10
    SITEMAP_PING_TIMEOUT = 15
    ARCHIVE_PING_TIMEOUT = 30
    
    # File paths
    DATA_DIR = 'data'
    RSS_FEEDS_DIR = 'data/rss_feeds'
    SITEMAPS_DIR = 'data/sitemaps'
    PING_LISTS_DIR = 'ping_lists'
    
    # Campaign settings
    MAX_URLS_PER_CAMPAIGN = 10000
    DEFAULT_RETRY_ATTEMPTS = 3
    RETRY_DELAY_SECONDS = 5
    
    # RSS feed settings
    RSS_TITLE_PREFIX = "SEO Backlink Feed"
    RSS_DESCRIPTION = "Automated RSS feed for backlink indexing"
    RSS_LANGUAGE = "en-us"
    
    # Sitemap settings
    SITEMAP_CHANGEFREQ = "daily"
    SITEMAP_PRIORITY = "0.8"
