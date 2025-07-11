from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from api_client import api_client
from auth import admin_required, is_admin_logged_in
import logging

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if is_admin_logged_in():
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'error')
            return render_template('admin/login.html')
        
        # Authenticate with API
        result = api_client.login_admin(username, password)
        
        if 'error' in result:
            flash(result['error'], 'error')
            return render_template('admin/login.html')
        
        # Store admin info in session
        session['admin_id'] = result.get('admin_id')
        session['admin_username'] = result.get('username', username)
        
        flash('تم تسجيل الدخول بنجاح', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@admin_required
def logout():
    """Admin logout"""
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    stats = api_client.get_stats()
    
    if 'error' in stats:
        flash('فشل في تحميل الإحصائيات', 'error')
        stats = {}
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@admin_required
def users():
    """Users management page"""
    page = request.args.get('page', 1, type=int)
    users_data = api_client.get_users(page=page)
    
    if 'error' in users_data:
        flash('فشل في تحميل المستخدمين', 'error')
        users_data = {'users': [], 'total': 0, 'pages': 0}
    
    return render_template('admin/users.html', 
                         users=users_data.get('users', []),
                         current_page=page,
                         total_pages=users_data.get('pages', 0),
                         total_users=users_data.get('total', 0))

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    result = api_client.toggle_user_status(user_id)
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('تم تحديث حالة المستخدم بنجاح', 'success')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    result = api_client.delete_user(user_id)
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('تم حذف المستخدم بنجاح', 'success')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/stores')
@admin_required
def stores():
    """Stores management page"""
    page = request.args.get('page', 1, type=int)
    stores_data = api_client.get_stores(page=page)
    
    if 'error' in stores_data:
        flash('فشل في تحميل المتاجر', 'error')
        stores_data = {'stores': [], 'total': 0, 'pages': 0}
    
    return render_template('admin/stores.html',
                         stores=stores_data.get('stores', []),
                         current_page=page,
                         total_pages=stores_data.get('pages', 0),
                         total_stores=stores_data.get('total', 0))

@admin_bp.route('/stores/<int:store_id>/delete', methods=['POST'])
@admin_required
def delete_store(store_id):
    """Delete store"""
    result = api_client.delete_store(store_id)
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('تم حذف المتجر بنجاح', 'success')
    
    return redirect(url_for('admin.stores'))

@admin_bp.route('/products')
@admin_required
def products():
    """Products management page"""
    page = request.args.get('page', 1, type=int)
    products_data = api_client.get_products(page=page)
    
    if 'error' in products_data:
        flash('فشل في تحميل المنتجات', 'error')
        products_data = {'products': [], 'total': 0, 'pages': 0}
    
    return render_template('admin/products.html',
                         products=products_data.get('products', []),
                         current_page=page,
                         total_pages=products_data.get('pages', 0),
                         total_products=products_data.get('total', 0))

@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    """Delete product"""
    result = api_client.delete_product(product_id)
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('تم حذف المنتج بنجاح', 'success')
    
    return redirect(url_for('admin.products'))

@admin_bp.route('/services')
@admin_required
def services():
    """Services management page"""
    page = request.args.get('page', 1, type=int)
    services_data = api_client.get_services(page=page)
    
    if 'error' in services_data:
        flash('فشل في تحميل الخدمات', 'error')
        services_data = {'services': [], 'total': 0, 'pages': 0}
    
    return render_template('admin/services.html',
                         services=services_data.get('services', []),
                         current_page=page,
                         total_pages=services_data.get('pages', 0),
                         total_services=services_data.get('total', 0))

@admin_bp.route('/services/<int:service_id>/delete', methods=['POST'])
@admin_required
def delete_service(service_id):
    """Delete service"""
    result = api_client.delete_service(service_id)
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('تم حذف الخدمة بنجاح', 'success')
    
    return redirect(url_for('admin.services'))

@admin_bp.route('/jobs')
@admin_required
def jobs():
    """Jobs management page"""
    page = request.args.get('page', 1, type=int)
    jobs_data = api_client.get_jobs(page=page)
    
    if 'error' in jobs_data:
        flash('فشل في تحميل الوظائف', 'error')
        jobs_data = {'jobs': [], 'total': 0, 'pages': 0}
    
    return render_template('admin/jobs.html',
                         jobs=jobs_data.get('jobs', []),
                         current_page=page,
                         total_pages=jobs_data.get('pages', 0),
                         total_jobs=jobs_data.get('total', 0))

@admin_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@admin_required
def delete_job(job_id):
    """Delete job"""
    result = api_client.delete_job(job_id)
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('تم حذف الوظيفة بنجاح', 'success')
    
    return redirect(url_for('admin.jobs'))

@admin_bp.route('/ads')
@admin_required
def ads():
    """Advertisements management page"""
    page = request.args.get('page', 1, type=int)
    ads_data = api_client.get_ads(page=page)
    
    if 'error' in ads_data:
        flash('فشل في تحميل الإعلانات', 'error')
        ads_data = {'ads': [], 'total': 0, 'pages': 0}
    
    return render_template('admin/ads.html',
                         ads=ads_data.get('ads', []),
                         current_page=page,
                         total_pages=ads_data.get('pages', 0),
                         total_ads=ads_data.get('total', 0))

@admin_bp.route('/ads/<int:ad_id>/delete', methods=['POST'])
@admin_required
def delete_ad(ad_id):
    """Delete advertisement"""
    result = api_client.delete_ad(ad_id)
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('تم حذف الإعلان بنجاح', 'success')
    
    return redirect(url_for('admin.ads'))
