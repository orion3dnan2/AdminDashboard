import os
import logging
from flask import Flask, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "bayt-al-sudani-secret-key-2025")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL environment variable is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
from models import db, User
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin.login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables and initialize default data
with app.app_context():
    db.create_all()
    # Initialize default admin user
    from auth import init_default_admin
    init_default_admin()

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
