from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user
from models import db, User, Store, Product, Service, Order, Advertisement, Job
from auth import admin_required, is_admin_logged_in, authenticate_user
from sqlalchemy import func, desc
import logging
from datetime import datetime

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
        
        # Authenticate with database
        user = authenticate_user(username, password, 'admin')
        
        if not user:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            return render_template('admin/login.html')
        
        # Login user using Flask-Login
        login_user(user, remember=True)
        
        flash('تم تسجيل الدخول بنجاح', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@admin_required
def logout():
    """Admin logout"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    try:
        # Get statistics from database
        stats = {
            'total_users': User.query.filter_by(role='merchant').count(),
            'total_admins': User.query.filter_by(role='admin').count(),
            'total_stores': Store.query.count(),
            'total_products': Product.query.count(),
            'total_services': Service.query.count(),
            'total_orders': Order.query.count(),
            'total_ads': Advertisement.query.count(),
            'total_jobs': Job.query.count(),
            'pending_orders': Order.query.filter_by(status='pending').count(),
            'active_stores': Store.query.filter_by(is_active=True).count(),
        }
        
        # Get recent activity
        recent_orders = Order.query.order_by(desc(Order.created_at)).limit(5).all()
        recent_products = Product.query.order_by(desc(Product.created_at)).limit(5).all()
        
        return render_template('admin/dashboard.html', 
                             stats=stats, 
                             recent_orders=recent_orders,
                             recent_products=recent_products,
                             now=datetime.now())
    except Exception as e:
        flash('فشل في تحميل الإحصائيات', 'error')
        logging.error(f"Dashboard stats error: {e}")
        return render_template('admin/dashboard.html', 
                             stats={'total_users': 0, 'total_stores': 0, 'total_products': 0, 'total_orders': 0, 'pending_orders': 0}, 
                             recent_orders=[], 
                             recent_products=[])

@admin_bp.route('/users')
@admin_required
def users():
    """Users management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    try:
        # Get users with pagination
        users_pagination = User.query.filter_by(role='merchant').paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_list = [user.to_dict() for user in users_pagination.items]
        
        return render_template('admin/users.html', 
                             users=users_list,
                             current_page=page,
                             total_pages=users_pagination.pages,
                             total_users=users_pagination.total,
                             has_prev=users_pagination.has_prev,
                             has_next=users_pagination.has_next,
                             prev_num=users_pagination.prev_num,
                             next_num=users_pagination.next_num)
    except Exception as e:
        flash('فشل في تحميل المستخدمين', 'error')
        logging.error(f"Users page error: {e}")
        return render_template('admin/users.html', 
                             users=[], current_page=1, total_pages=0, total_users=0)

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        user = User.query.get_or_404(user_id)
        if user.role != 'merchant':
            flash('لا يمكن تغيير حالة هذا المستخدم', 'error')
            return redirect(url_for('admin.users'))
        
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'تم تفعيل' if user.is_active else 'تم إلغاء تفعيل'
        flash(f'{status} المستخدم بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('فشل في تحديث حالة المستخدم', 'error')
        logging.error(f"Toggle user status error: {e}")
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    try:
        user = User.query.get_or_404(user_id)
        if user.role != 'merchant':
            flash('لا يمكن حذف هذا المستخدم', 'error')
            return redirect(url_for('admin.users'))
        
        # Delete related stores, products, orders
        stores = Store.query.filter_by(merchant_id=user_id).all()
        for store in stores:
            db.session.delete(store)
        
        db.session.delete(user)
        db.session.commit()
        
        flash('تم حذف المستخدم وجميع بياناته بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('فشل في حذف المستخدم', 'error')
        logging.error(f"Delete user error: {e}")
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/stores')
@admin_required
def stores():
    """Stores management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    try:
        # Get stores with pagination
        stores_pagination = Store.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        stores_list = [store.to_dict() for store in stores_pagination.items]
        
        return render_template('admin/stores.html',
                             stores=stores_list,
                             current_page=page,
                             total_pages=stores_pagination.pages,
                             total_stores=stores_pagination.total,
                             has_prev=stores_pagination.has_prev,
                             has_next=stores_pagination.has_next,
                             prev_num=stores_pagination.prev_num,
                             next_num=stores_pagination.next_num)
    except Exception as e:
        flash('فشل في تحميل المتاجر', 'error')
        logging.error(f"Stores page error: {e}")
        return render_template('admin/stores.html', 
                             stores=[], current_page=1, total_pages=0, total_stores=0)

@admin_bp.route('/stores/<int:store_id>/delete', methods=['POST'])
@admin_required
def delete_store(store_id):
    """Delete store"""
    try:
        store = Store.query.get_or_404(store_id)
        
        # Delete related products and services
        products = Product.query.filter_by(store_id=store_id).all()
        services = Service.query.filter_by(store_id=store_id).all()
        
        for product in products:
            db.session.delete(product)
        for service in services:
            db.session.delete(service)
        
        db.session.delete(store)
        db.session.commit()
        
        flash('تم حذف المتجر وجميع منتجاته بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('فشل في حذف المتجر', 'error')
        logging.error(f"Delete store error: {e}")
    
    return redirect(url_for('admin.stores'))

@admin_bp.route('/products')
@admin_required
def products():
    """Products management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    try:
        # Get products with pagination
        products_pagination = Product.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        products_list = [product.to_dict() for product in products_pagination.items]
        
        return render_template('admin/products.html',
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
        return render_template('admin/products.html', 
                             products=[], current_page=1, total_pages=0, total_products=0)

@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    """Delete product"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # Delete related orders
        orders = Order.query.filter_by(product_id=product_id).all()
        for order in orders:
            db.session.delete(order)
        
        db.session.delete(product)
        db.session.commit()
        
        flash('تم حذف المنتج وجميع طلباته بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('فشل في حذف المنتج', 'error')
        logging.error(f"Delete product error: {e}")
    
    return redirect(url_for('admin.products'))

@admin_bp.route('/services')
@admin_required
def services():
    """Services management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    try:
        # Get services with pagination
        services_pagination = Service.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        services_list = [service.to_dict() for service in services_pagination.items]
        
        return render_template('admin/services.html',
                             services=services_list,
                             current_page=page,
                             total_pages=services_pagination.pages,
                             total_services=services_pagination.total,
                             has_prev=services_pagination.has_prev,
                             has_next=services_pagination.has_next,
                             prev_num=services_pagination.prev_num,
                             next_num=services_pagination.next_num)
    except Exception as e:
        flash('فشل في تحميل الخدمات', 'error')
        logging.error(f"Services page error: {e}")
        return render_template('admin/services.html', 
                             services=[], current_page=1, total_pages=0, total_services=0)

@admin_bp.route('/services/<int:service_id>/delete', methods=['POST'])
@admin_required
def delete_service(service_id):
    """Delete service"""
    try:
        service = Service.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        
        flash('تم حذف الخدمة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('فشل في حذف الخدمة', 'error')
        logging.error(f"Delete service error: {e}")
    
    return redirect(url_for('admin.services'))

@admin_bp.route('/jobs')
@admin_required
def jobs():
    """Jobs management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    try:
        # Get jobs with pagination
        jobs_pagination = Job.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        jobs_list = [job.to_dict() for job in jobs_pagination.items]
        
        return render_template('admin/jobs.html',
                             jobs=jobs_list,
                             current_page=page,
                             total_pages=jobs_pagination.pages,
                             total_jobs=jobs_pagination.total,
                             has_prev=jobs_pagination.has_prev,
                             has_next=jobs_pagination.has_next,
                             prev_num=jobs_pagination.prev_num,
                             next_num=jobs_pagination.next_num)
    except Exception as e:
        flash('فشل في تحميل الوظائف', 'error')
        logging.error(f"Jobs page error: {e}")
        return render_template('admin/jobs.html', 
                             jobs=[], current_page=1, total_pages=0, total_jobs=0)

@admin_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@admin_required
def delete_job(job_id):
    """Delete job"""
    try:
        job = Job.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        
        flash('تم حذف الوظيفة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('فشل في حذف الوظيفة', 'error')
        logging.error(f"Delete job error: {e}")
    
    return redirect(url_for('admin.jobs'))

@admin_bp.route('/ads')
@admin_required
def ads():
    """Advertisements management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    try:
        # Get ads with pagination
        ads_pagination = Advertisement.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        ads_list = [ad.to_dict() for ad in ads_pagination.items]
        
        return render_template('admin/ads.html',
                             ads=ads_list,
                             current_page=page,
                             total_pages=ads_pagination.pages,
                             total_ads=ads_pagination.total,
                             has_prev=ads_pagination.has_prev,
                             has_next=ads_pagination.has_next,
                             prev_num=ads_pagination.prev_num,
                             next_num=ads_pagination.next_num)
    except Exception as e:
        flash('فشل في تحميل الإعلانات', 'error')
        logging.error(f"Ads page error: {e}")
        return render_template('admin/ads.html', 
                             ads=[], current_page=1, total_pages=0, total_ads=0)

@admin_bp.route('/ads/<int:ad_id>/delete', methods=['POST'])
@admin_required
def delete_ad(ad_id):
    """Delete advertisement"""
    try:
        ad = Advertisement.query.get_or_404(ad_id)
        db.session.delete(ad)
        db.session.commit()
        
        flash('تم حذف الإعلان بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('فشل في حذف الإعلان', 'error')
        logging.error(f"Delete ad error: {e}")
    
    return redirect(url_for('admin.ads'))

# ==================== COMPREHENSIVE ADMIN MANAGEMENT ROUTES ====================

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Add new user (merchant)"""
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role', 'merchant')
            
            if not username or not email or not password:
                flash('جميع الحقول مطلوبة', 'error')
                return render_template('admin/add_user.html')
            
            # Check if user exists
            if User.query.filter_by(username=username).first():
                flash('اسم المستخدم موجود بالفعل', 'error')
                return render_template('admin/add_user.html')
            
            if User.query.filter_by(email=email).first():
                flash('البريد الإلكتروني موجود بالفعل', 'error')
                return render_template('admin/add_user.html')
            
            # Create new user
            new_user = User(
                username=username,
                email=email,
                role=role,
                is_active=True
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'تم إنشاء المستخدم {username} بنجاح', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding user: {str(e)}")
            flash('حدث خطأ أثناء إنشاء المستخدم', 'error')
    
    return render_template('admin/add_user.html')

@admin_bp.route('/stores/add', methods=['GET', 'POST'])
@admin_required
def add_store():
    """Add new store"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description', '')
            merchant_id = request.form.get('merchant_id')
            
            if not name or not merchant_id:
                flash('اسم المتجر ومعرف التاجر مطلوبان', 'error')
                merchants = User.query.filter_by(role='merchant').all()
                return render_template('admin/add_store.html', merchants=merchants)
            
            # Check if merchant exists
            merchant = User.query.filter_by(id=merchant_id, role='merchant').first()
            if not merchant:
                flash('التاجر المحدد غير موجود', 'error')
                merchants = User.query.filter_by(role='merchant').all()
                return render_template('admin/add_store.html', merchants=merchants)
            
            # Create new store
            new_store = Store(
                name=name,
                description=description,
                merchant_id=merchant_id,
                is_active=True
            )
            
            db.session.add(new_store)
            db.session.commit()
            
            flash(f'تم إنشاء المتجر {name} بنجاح', 'success')
            return redirect(url_for('admin.stores'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding store: {str(e)}")
            flash('حدث خطأ أثناء إنشاء المتجر', 'error')
    
    merchants = User.query.filter_by(role='merchant').all()
    return render_template('admin/add_store.html', merchants=merchants)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    """Add new product"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description', '')
            price = request.form.get('price')
            store_id = request.form.get('store_id')
            
            if not name or not price or not store_id:
                flash('اسم المنتج والسعر والمتجر مطلوبة', 'error')
                stores = Store.query.filter_by(is_active=True).all()
                return render_template('admin/add_product.html', stores=stores)
            
            # Validate price
            try:
                price = float(price)
                if price < 0:
                    raise ValueError()
            except ValueError:
                flash('السعر يجب أن يكون رقماً موجباً', 'error')
                stores = Store.query.filter_by(is_active=True).all()
                return render_template('admin/add_product.html', stores=stores)
            
            # Check if store exists
            store = Store.query.get(store_id)
            if not store:
                flash('المتجر المحدد غير موجود', 'error')
                stores = Store.query.filter_by(is_active=True).all()
                return render_template('admin/add_product.html', stores=stores)
            
            # Create new product
            new_product = Product(
                name=name,
                description=description,
                price=price,
                store_id=store_id,
                merchant_id=store.merchant_id,
                is_active=True
            )
            
            db.session.add(new_product)
            db.session.commit()
            
            flash(f'تم إنشاء المنتج {name} بنجاح', 'success')
            return redirect(url_for('admin.products'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding product: {str(e)}")
            flash('حدث خطأ أثناء إنشاء المنتج', 'error')
    
    stores = Store.query.filter_by(is_active=True).all()
    return render_template('admin/add_product.html', stores=stores)

@admin_bp.route('/services/add', methods=['GET', 'POST'])
@admin_required
def add_service():
    """Add new service"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description', '')
            price = request.form.get('price')
            store_id = request.form.get('store_id')
            
            if not name or not price or not store_id:
                flash('اسم الخدمة والسعر والمتجر مطلوبة', 'error')
                stores = Store.query.filter_by(is_active=True).all()
                return render_template('admin/add_service.html', stores=stores)
            
            # Validate price
            try:
                price = float(price)
                if price < 0:
                    raise ValueError()
            except ValueError:
                flash('السعر يجب أن يكون رقماً موجباً', 'error')
                stores = Store.query.filter_by(is_active=True).all()
                return render_template('admin/add_service.html', stores=stores)
            
            # Check if store exists
            store = Store.query.get(store_id)
            if not store:
                flash('المتجر المحدد غير موجود', 'error')
                stores = Store.query.filter_by(is_active=True).all()
                return render_template('admin/add_service.html', stores=stores)
            
            # Create new service
            new_service = Service(
                name=name,
                description=description,
                price=price,
                store_id=store_id,
                is_active=True
            )
            
            db.session.add(new_service)
            db.session.commit()
            
            flash(f'تم إنشاء الخدمة {name} بنجاح', 'success')
            return redirect(url_for('admin.services'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding service: {str(e)}")
            flash('حدث خطأ أثناء إنشاء الخدمة', 'error')
    
    stores = Store.query.filter_by(is_active=True).all()
    return render_template('admin/add_service.html', stores=stores)

@admin_bp.route('/ads/add', methods=['GET', 'POST'])
@admin_required
def add_advertisement():
    """Add new advertisement"""
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            description = request.form.get('description', '')
            image_url = request.form.get('image_url', '')
            
            if not title:
                flash('عنوان الإعلان مطلوب', 'error')
                return render_template('admin/add_advertisement.html')
            
            # Create new advertisement
            new_ad = Advertisement(
                title=title,
                description=description,
                image_url=image_url,
                is_active=True
            )
            
            db.session.add(new_ad)
            db.session.commit()
            
            flash(f'تم إنشاء الإعلان {title} بنجاح', 'success')
            return redirect(url_for('admin.ads'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding advertisement: {str(e)}")
            flash('حدث خطأ أثناء إنشاء الإعلان', 'error')
    
    return render_template('admin/add_advertisement.html')

@admin_bp.route('/jobs/add', methods=['GET', 'POST'])
@admin_required
def add_job():
    """Add new job posting"""
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            description = request.form.get('description', '')
            company = request.form.get('company')
            location = request.form.get('location', '')
            salary = request.form.get('salary', '')
            
            if not title or not company:
                flash('عنوان الوظيفة واسم الشركة مطلوبان', 'error')
                return render_template('admin/add_job.html')
            
            # Create new job
            new_job = Job(
                title=title,
                description=description,
                company=company,
                location=location,
                salary=salary,
                is_active=True
            )
            
            db.session.add(new_job)
            db.session.commit()
            
            flash(f'تم إنشاء الوظيفة {title} بنجاح', 'success')
            return redirect(url_for('admin.jobs'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding job: {str(e)}")
            flash('حدث خطأ أثناء إنشاء الوظيفة', 'error')
    
    return render_template('admin/add_job.html')

@admin_bp.route('/approve_merchant/<int:user_id>', methods=['POST'])
@admin_required
def approve_merchant(user_id):
    """Approve merchant registration"""
    try:
        user = User.query.get_or_404(user_id)
        
        if user.role != 'merchant':
            flash('هذا المستخدم ليس تاجراً', 'error')
            return redirect(url_for('admin.users'))
        
        user.is_active = True
        db.session.commit()
        
        flash(f'تم اعتماد التاجر {user.username} بنجاح', 'success')
        return redirect(url_for('admin.users'))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error approving merchant: {str(e)}")
        flash('حدث خطأ أثناء اعتماد التاجر', 'error')
        return redirect(url_for('admin.users'))

@admin_bp.route('/manage_subscriptions')
@admin_required
def manage_subscriptions():
    """Manage merchant subscriptions"""
    try:
        merchants = User.query.filter_by(role='merchant').all()
        return render_template('admin/subscriptions.html', merchants=merchants)
        
    except Exception as e:
        logging.error(f"Error in subscriptions management: {str(e)}")
        flash('حدث خطأ في تحميل الاشتراكات', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/approve_subscription/<int:user_id>', methods=['POST'])
@admin_required
def approve_subscription(user_id):
    """Approve subscription renewal"""
    try:
        user = User.query.get_or_404(user_id)
        
        if user.role != 'merchant':
            flash('هذا المستخدم ليس تاجراً', 'error')
            return redirect(url_for('admin.manage_subscriptions'))
        
        # Here you can add subscription logic
        flash(f'تم تجديد اشتراك {user.username} بنجاح', 'success')
        return redirect(url_for('admin.manage_subscriptions'))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error approving subscription: {str(e)}")
        flash('حدث خطأ أثناء تجديد الاشتراك', 'error')
        return redirect(url_for('admin.manage_subscriptions'))

@admin_bp.route('/approve_job/<int:job_id>', methods=['POST'])
@admin_required
def approve_job(job_id):
    """Approve job posting"""
    try:
        job = Job.query.get_or_404(job_id)
        job.is_active = True
        db.session.commit()
        
        flash(f'تم اعتماد الوظيفة {job.title} بنجاح', 'success')
        return redirect(url_for('admin.jobs'))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error approving job: {str(e)}")
        flash('حدث خطأ أثناء اعتماد الوظيفة', 'error')
        return redirect(url_for('admin.jobs'))

@admin_bp.route('/reject_job/<int:job_id>', methods=['POST'])
@admin_required
def reject_job(job_id):
    """Reject job posting"""
    try:
        job = Job.query.get_or_404(job_id)
        job.is_active = False
        db.session.commit()
        
        flash(f'تم رفض الوظيفة {job.title}', 'warning')
        return redirect(url_for('admin.jobs'))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error rejecting job: {str(e)}")
        flash('حدث خطأ أثناء رفض الوظيفة', 'error')
        return redirect(url_for('admin.jobs'))
