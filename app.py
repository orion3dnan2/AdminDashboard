import os
import logging
from flask import Flask, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "bayt-al-sudani-secret-key-2025")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Import and register blueprints
from admin_routes import admin_bp
from merchant_routes import merchant_bp

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(merchant_bp, url_prefix='/merchant')

@app.route('/')
def index():
    """Root route redirects to admin login"""
    return redirect(url_for('admin.login'))

@app.errorhandler(404)
def not_found(error):
    return redirect(url_for('admin.login'))

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return "خطأ في الخادم. يرجى المحاولة لاحقاً.", 500
