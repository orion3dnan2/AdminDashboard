from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from api_client import api_client
from auth import merchant_required, is_merchant_logged_in, get_current_merchant
import logging

merchant_bp = Blueprint('merchant', __name__)

@merchant_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Merchant login page"""
    if is_merchant_logged_in():
        return redirect(url_for('merchant.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('يرجى إدخال البريد الإلكتروني وكلمة المرور', 'error')
            return render_template('merchant/login.html')
        
        # Authenticate with API
        result = api_client.login_merchant(email, password)
        
        if 'error' in result:
            flash(result['error'], 'error')
            return render_template('merchant/login.html')
        
        # Store merchant info in session
        session['merchant_id'] = result.get('merchant_id')
        session['merchant_email'] = result.get('email', email)
        session['merchant_store_id'] = result.get('store_id')
        
        flash('تم تسجيل الدخول بنجاح', 'success')
        return redirect(url_for('merchant.dashboard'))
    
    return render_template('merchant/login.html')

@merchant_bp.route('/logout')
@merchant_required
def logout():
    """Merchant logout"""
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('merchant.login'))

@merchant_bp.route('/dashboard')
@merchant_required
def dashboard():
    """Merchant dashboard"""
    merchant = get_current_merchant()
    
    # Get store info
    store_data = {}
    if merchant['store_id']:
        store_result = api_client.get_store(merchant['store_id'])
        if 'error' not in store_result:
            store_data = store_result
    
    # Get products count
    products_result = api_client.get_products(store_id=merchant['store_id'], limit=1)
    products_count = products_result.get('total', 0) if 'error' not in products_result else 0
    
    # Get services count
    services_result = api_client.get_services(store_id=merchant['store_id'], limit=1)
    services_count = services_result.get('total', 0) if 'error' not in services_result else 0
    
    # Get orders count
    orders_result = api_client.get_orders(store_id=merchant['store_id'], limit=1)
    orders_count = orders_result.get('total', 0) if 'error' not in orders_result else 0
    
    # Get subscription info
    subscription_result = api_client.get_subscription(merchant['id'])
    subscription = subscription_result if 'error' not in subscription_result else {}
    
    stats = {
        'products_count': products_count,
        'services_count': services_count,
        'orders_count': orders_count
    }
    
    return render_template('merchant/dashboard.html', 
                         store=store_data, 
                         stats=stats,
                         subscription=subscription)

@merchant_bp.route('/store-profile', methods=['GET', 'POST'])
@merchant_required
def store_profile():
    """Store profile management"""
    merchant = get_current_merchant()
    
    if not merchant['store_id']:
        flash('لا يوجد متجر مرتبط بحسابك', 'error')
        return redirect(url_for('merchant.dashboard'))
    
    if request.method == 'POST':
        # Update store data
        store_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'address': request.form.get('address'),
            'phone': request.form.get('phone'),
            'category': request.form.get('category')
        }
        
        result = api_client.update_store(merchant['store_id'], store_data)
        
        if 'error' in result:
            flash(result['error'], 'error')
        else:
            flash('تم تحديث بيانات المتجر بنجاح', 'success')
        
        return redirect(url_for('merchant.store_profile'))
    
    # Get store data
    store_result = api_client.get_store(merchant['store_id'])
    
    if 'error' in store_result:
        flash('فشل في تحميل بيانات المتجر', 'error')
        store_result = {}
    
    return render_template('merchant/store_profile.html', store=store_result)

@merchant_bp.route('/products')
@merchant_required
def products():
    """Merchant products management"""
    merchant = get_current_merchant()
    page = request.args.get('page', 1, type=int)
    
    products_data = api_client.get_products(page=page, store_id=merchant['store_id'])
    
    if 'error' in products_data:
        flash('فشل في تحميل المنتجات', 'error')
        products_data = {'products': [], 'total': 0, 'pages': 0}
    
    return render_template('merchant/products.html',
                         products=products_data.get('products', []),
                         current_page=page,
                         total_pages=products_data.get('pages', 0),
                         total_products=products_data.get('total', 0))

@merchant_bp.route('/products/add', methods=['GET', 'POST'])
@merchant_required
def add_product():
    """Add new product"""
    merchant = get_current_merchant()
    
    if request.method == 'POST':
        product_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price', 0)),
            'category': request.form.get('category'),
            'store_id': merchant['store_id']
        }
        
        result = api_client.create_product(product_data)
        
        if 'error' in result:
            flash(result['error'], 'error')
        else:
            flash('تم إضافة المنتج بنجاح', 'success')
            return redirect(url_for('merchant.products'))
    
    return render_template('merchant/products.html', add_mode=True)

@merchant_bp.route('/products/<int:product_id>/edit', methods=['POST'])
@merchant_required
def edit_product(product_id):
    """Edit product"""
    product_data = {
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'price': float(request.form.get('price', 0)),
        'category': request.form.get('category')
    }
    
    result = api_client.update_product(product_id, product_data)
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('تم تحديث المنتج بنجاح', 'success')
    
    return redirect(url_for('merchant.products'))

@merchant_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@merchant_required
def delete_product(product_id):
    """Delete product"""
    result = api_client.delete_product(product_id)
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('تم حذف المنتج بنجاح', 'success')
    
    return redirect(url_for('merchant.products'))

@merchant_bp.route('/services')
@merchant_required
def services():
    """Merchant services management"""
    merchant = get_current_merchant()
    page = request.args.get('page', 1, type=int)
    
    services_data = api_client.get_services(page=page, store_id=merchant['store_id'])
    
    if 'error' in services_data:
        flash('فشل في تحميل الخدمات', 'error')
        services_data = {'services': [], 'total': 0, 'pages': 0}
    
    return render_template('merchant/services.html',
                         services=services_data.get('services', []),
                         current_page=page,
                         total_pages=services_data.get('pages', 0),
                         total_services=services_data.get('total', 0))

@merchant_bp.route('/services/add', methods=['POST'])
@merchant_required
def add_service():
    """Add new service"""
    merchant = get_current_merchant()
    
    service_data = {
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'price': float(request.form.get('price', 0)),
        'category': request.form.get('category'),
        'store_id': merchant['store_id']
    }
    
    result = api_client.create_service(service_data)
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('تم إضافة الخدمة بنجاح', 'success')
    
    return redirect(url_for('merchant.services'))

@merchant_bp.route('/services/<int:service_id>/delete', methods=['POST'])
@merchant_required
def delete_service(service_id):
    """Delete service"""
    result = api_client.delete_service(service_id)
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('تم حذف الخدمة بنجاح', 'success')
    
    return redirect(url_for('merchant.services'))

@merchant_bp.route('/orders')
@merchant_required
def orders():
    """Merchant orders management"""
    merchant = get_current_merchant()
    page = request.args.get('page', 1, type=int)
    
    orders_data = api_client.get_orders(store_id=merchant['store_id'], page=page)
    
    if 'error' in orders_data:
        flash('فشل في تحميل الطلبات', 'error')
        orders_data = {'orders': [], 'total': 0, 'pages': 0}
    
    return render_template('merchant/orders.html',
                         orders=orders_data.get('orders', []),
                         current_page=page,
                         total_pages=orders_data.get('pages', 0),
                         total_orders=orders_data.get('total', 0))

@merchant_bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
@merchant_required
def update_order_status(order_id):
    """Update order status"""
    status = request.form.get('status')
    
    result = api_client.update_order_status(order_id, status)
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('تم تحديث حالة الطلب بنجاح', 'success')
    
    return redirect(url_for('merchant.orders'))

@merchant_bp.route('/subscription')
@merchant_required
def subscription():
    """Merchant subscription management"""
    merchant = get_current_merchant()
    
    subscription_result = api_client.get_subscription(merchant['id'])
    subscription_data = subscription_result if 'error' not in subscription_result else {}
    
    history_result = api_client.get_subscription_history(merchant['id'])
    history_data = history_result.get('history', []) if 'error' not in history_result else []
    
    return render_template('merchant/subscription.html',
                         subscription=subscription_data,
                         history=history_data)
