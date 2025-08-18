import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import routes after app creation to avoid circular imports
from routes import *

# Ensure data directories exist
os.makedirs('data/rss_feeds', exist_ok=True)
os.makedirs('data/sitemaps', exist_ok=True)
os.makedirs('ping_lists', exist_ok=True)
