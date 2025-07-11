from functools import wraps
from flask import session, redirect, url_for, request, flash

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('يجب تسجيل الدخول كمدير أولاً', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def merchant_required(f):
    """Decorator to require merchant authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'merchant_id' not in session:
            flash('يجب تسجيل الدخول كتاجر أولاً', 'error')
            return redirect(url_for('merchant.login'))
        return f(*args, **kwargs)
    return decorated_function

def is_admin_logged_in():
    """Check if admin is logged in"""
    return 'admin_id' in session

def is_merchant_logged_in():
    """Check if merchant is logged in"""
    return 'merchant_id' in session

def get_current_admin():
    """Get current admin info from session"""
    if is_admin_logged_in():
        return {
            'id': session.get('admin_id'),
            'username': session.get('admin_username')
        }
    return None

def get_current_merchant():
    """Get current merchant info from session"""
    if is_merchant_logged_in():
        return {
            'id': session.get('merchant_id'),
            'email': session.get('merchant_email'),
            'store_id': session.get('merchant_store_id')
        }
    return None
