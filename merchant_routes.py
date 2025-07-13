from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from models import db, User, Store, Product, Service, Order
from auth import merchant_required, is_merchant_logged_in, authenticate_user
from sqlalchemy import func, desc
from decimal import Decimal
import logging

merchant_bp = Blueprint('merchant', __name__)

@merchant_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Merchant login page"""
    if is_merchant_logged_in():
        return redirect(url_for('merchant.dashboard'))
    
    if request.method == 'POST':
        email_or_username = request.form.get('email')
        password = request.form.get('password')
        
        if not email_or_username or not password:
            flash('يرجى إدخال البريد الإلكتروني أو اسم المستخدم وكلمة المرور', 'error')
            return render_template('merchant/login.html')
        
        # Authenticate with database
        user = authenticate_user(email_or_username, password, 'merchant')
        
        if not user:
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة', 'error')
            return render_template('merchant/login.html')
        
        # Login user using Flask-Login
        login_user(user, remember=True)
        
        flash('تم تسجيل الدخول بنجاح', 'success')
        return redirect(url_for('merchant.dashboard'))
    
    return render_template('merchant/login.html')

@merchant_bp.route('/logout')
@merchant_required
def logout():
    """Merchant logout"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('merchant.login'))

@merchant_bp.route('/dashboard')
@merchant_required
def dashboard():
    """Merchant dashboard"""
    try:
        merchant = current_user
        
        # Get or create store for merchant
        store = Store.query.filter_by(merchant_id=merchant.id).first()
        if not store:
            # Create default store for merchant
            store = Store(
                name=f"متجر {merchant.username}",
                description="متجر جديد",
                merchant_id=merchant.id
            )
            db.session.add(store)
            db.session.commit()
        
        # Get statistics
        stats = {
            'products_count': Product.query.filter_by(merchant_id=merchant.id).count(),
            'services_count': Service.query.filter_by(store_id=store.id).count(),
            'orders_count': Order.query.filter_by(merchant_id=merchant.id).count(),
            'pending_orders': Order.query.filter_by(merchant_id=merchant.id, status='pending').count(),
            'total_revenue': db.session.query(func.sum(Order.total_price)).filter_by(
                merchant_id=merchant.id, status='delivered'
            ).scalar() or 0
        }
        
        # Get recent orders
        recent_orders = Order.query.filter_by(merchant_id=merchant.id).order_by(
            desc(Order.created_at)
        ).limit(5).all()
        
        # Get recent products
        recent_products = Product.query.filter_by(merchant_id=merchant.id).order_by(
            desc(Product.created_at)
        ).limit(5).all()
        
        return render_template('merchant/dashboard.html',
                             store=store,
                             stats=stats,
                             recent_orders=recent_orders,
                             recent_products=recent_products)
    except Exception as e:
        flash('فشل في تحميل لوحة التحكم', 'error')
        logging.error(f"Merchant dashboard error: {e}")
        return render_template('merchant/dashboard.html', 
                             store=None, stats={}, recent_orders=[], recent_products=[])

@merchant_bp.route('/store-profile', methods=['GET', 'POST'])
@merchant_required
def store_profile():
    """Store profile management"""
    try:
        merchant = current_user
        store = Store.query.filter_by(merchant_id=merchant.id).first()
        
        if not store:
            flash('لا يوجد متجر مرتبط بحسابك', 'error')
            return redirect(url_for('merchant.dashboard'))
        
        if request.method == 'POST':
            # Update store data
            store.name = request.form.get('name', store.name)
            store.description = request.form.get('description', store.description)
            
            try:
                db.session.commit()
                flash('تم تحديث بيانات المتجر بنجاح', 'success')
            except Exception as e:
                db.session.rollback()
                flash('فشل في تحديث بيانات المتجر', 'error')
                logging.error(f"Store update error: {e}")
            
            return redirect(url_for('merchant.store_profile'))
        
        return render_template('merchant/store_profile.html', store=store)
    except Exception as e:
        flash('فشل في تحميل بيانات المتجر', 'error')
        logging.error(f"Store profile error: {e}")
        return redirect(url_for('merchant.dashboard'))

@merchant_bp.route('/products')
@merchant_required
def products():
    """Merchant products management"""
    try:
        merchant = current_user
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Get products with pagination
        products_pagination = Product.query.filter_by(merchant_id=merchant.id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        products_list = [product.to_dict() for product in products_pagination.items]
        
        return render_template('merchant/products.html',
                             products=products_list,
                             current_page=page,
                             total_pages=products_pagination.pages,
                             total_products=products_pagination.total,
                             has_prev=products_pagination.has_prev,
                             has_next=products_pagination.has_next,
                             prev_num=products_pagination.prev_num,
                             next_num=products_pagination.next_num)
    except Exception as e:
        flash('فشل في تحميل المنتجات', 'error')
        logging.error(f"Products page error: {e}")
        return render_template('merchant/products.html', 
                             products=[], current_page=1, total_pages=0, total_products=0)

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
