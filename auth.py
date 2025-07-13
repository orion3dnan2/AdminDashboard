"""
Authentication and authorization module for BaytAlSudani Admin Dashboard
"""
from functools import wraps
from flask import session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import User, db

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('يجب تسجيل الدخول كمدير أولاً', 'error')
            return redirect(url_for('admin.login'))
        
        if not current_user.is_admin():
            flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('admin.login'))
        
        if not current_user.is_active:
            flash('حسابك معطل، يرجى التواصل مع الإدارة', 'error')
            return redirect(url_for('admin.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def merchant_required(f):
    """Decorator to require merchant authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('يجب تسجيل الدخول كتاجر أولاً', 'error')
            return redirect(url_for('merchant.login'))
        
        if not current_user.is_merchant():
            flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('merchant.login'))
        
        if not current_user.is_active:
            flash('حسابك معطل، يرجى التواصل مع الإدارة', 'error')
            return redirect(url_for('merchant.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def authenticate_user(username_or_email, password, role):
    """Authenticate user with database"""
    try:
        # Try to find user by username or email
        user = User.query.filter(
            db.or_(
                User.username == username_or_email,
                User.email == username_or_email
            ),
            User.role == role,
            User.is_active == True
        ).first()
        
        if user and user.check_password(password):
            return user
        return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def create_admin_user(username, password, email=None):
    """Create admin user"""
    try:
        existing_user = User.query.filter(
            db.or_(User.username == username, User.email == email)
        ).first()
        
        if existing_user:
            return None, 'المستخدم موجود بالفعل'
        
        admin = User(
            username=username,
            email=email,
            role='admin'
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        return admin, None
    except Exception as e:
        db.session.rollback()
        return None, f'خطأ في إنشاء المستخدم: {str(e)}'

def create_merchant_user(username, email, password):
    """Create merchant user"""
    try:
        existing_user = User.query.filter(
            db.or_(User.username == username, User.email == email)
        ).first()
        
        if existing_user:
            return None, 'المستخدم موجود بالفعل'
        
        merchant = User(
            username=username,
            email=email,
            role='merchant'
        )
        merchant.set_password(password)
        
        db.session.add(merchant)
        db.session.commit()
        
        return merchant, None
    except Exception as e:
        db.session.rollback()
        return None, f'خطأ في إنشاء المستخدم: {str(e)}'

def is_admin_logged_in():
    """Check if admin is logged in"""
    return current_user.is_authenticated and current_user.is_admin()

def is_merchant_logged_in():
    """Check if merchant is logged in"""
    return current_user.is_authenticated and current_user.is_merchant()

def get_current_admin():
    """Get current admin info"""
    if is_admin_logged_in():
        return current_user
    return None

def get_current_merchant():
    """Get current merchant info"""
    if is_merchant_logged_in():
        return current_user
    return None

def init_default_admin():
    """Initialize default admin user if no admin exists"""
    try:
        admin_exists = User.query.filter_by(role='admin').first()
        if not admin_exists:
            admin, error = create_admin_user(
                username='admin',
                password='admin123',
                email='admin@baytsudani.com'
            )
            if admin:
                print("Default admin user created: admin/admin123")
                return True
            else:
                print(f"Failed to create default admin: {error}")
                return False
        return True
    except Exception as e:
        print(f"Error initializing admin: {e}")
        return False
