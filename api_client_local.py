"""
Local API Client for BaytAlSudani Admin Dashboard
Provides internal API endpoints for the dashboard
"""
from flask import jsonify, request
from models import db, User, Store, Product, Service, Order, Advertisement, Job
from auth import authenticate_user
from sqlalchemy import func

class LocalAPIClient:
    """Local API client for internal operations"""
    
    @staticmethod
    def login_admin(username, password):
        """Admin login"""
        user = authenticate_user(username, password, 'admin')
        if user:
            return {
                'admin_id': user.id,
                'username': user.username,
                'email': user.email
            }
        return {'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'}
    
    @staticmethod
    def login_merchant(email, password):
        """Merchant login"""
        user = authenticate_user(email, password, 'merchant')
        if user:
            store = Store.query.filter_by(merchant_id=user.id).first()
            return {
                'merchant_id': user.id,
                'username': user.username,
                'email': user.email,
                'store_id': store.id if store else None
            }
        return {'error': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'}
    
    @staticmethod
    def get_users(page=1, limit=20):
        """Get users with pagination"""
        try:
            pagination = User.query.filter_by(role='merchant').paginate(
                page=page, per_page=limit, error_out=False
            )
            
            return {
                'users': [user.to_dict() for user in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            }
        except Exception as e:
            return {'error': f'فشل في جلب المستخدمين: {str(e)}'}
    
    @staticmethod
    def get_stores(page=1, limit=20):
        """Get stores with pagination"""
        try:
            pagination = Store.query.paginate(
                page=page, per_page=limit, error_out=False
            )
            
            return {
                'stores': [store.to_dict() for store in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            }
        except Exception as e:
            return {'error': f'فشل في جلب المتاجر: {str(e)}'}
    
    @staticmethod
    def get_products(page=1, limit=20, store_id=None):
        """Get products with pagination"""
        try:
            query = Product.query
            if store_id:
                query = query.filter_by(store_id=store_id)
            
            pagination = query.paginate(
                page=page, per_page=limit, error_out=False
            )
            
            return {
                'products': [product.to_dict() for product in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            }
        except Exception as e:
            return {'error': f'فشل في جلب المنتجات: {str(e)}'}
    
    @staticmethod
    def get_services(page=1, limit=20, store_id=None):
        """Get services with pagination"""
        try:
            query = Service.query
            if store_id:
                query = query.filter_by(store_id=store_id)
            
            pagination = query.paginate(
                page=page, per_page=limit, error_out=False
            )
            
            return {
                'services': [service.to_dict() for service in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            }
        except Exception as e:
            return {'error': f'فشل في جلب الخدمات: {str(e)}'}
    
    @staticmethod
    def get_orders(page=1, limit=20, store_id=None, merchant_id=None):
        """Get orders with pagination"""
        try:
            query = Order.query
            if merchant_id:
                query = query.filter_by(merchant_id=merchant_id)
            elif store_id:
                # Get orders for products in this store
                query = query.join(Product).filter(Product.store_id == store_id)
            
            pagination = query.paginate(
                page=page, per_page=limit, error_out=False
            )
            
            return {
                'orders': [order.to_dict() for order in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            }
        except Exception as e:
            return {'error': f'فشل في جلب الطلبات: {str(e)}'}
    
    @staticmethod
    def get_stats():
        """Get dashboard statistics"""
        try:
            return {
                'total_users': User.query.filter_by(role='merchant').count(),
                'total_admins': User.query.filter_by(role='admin').count(),
                'total_stores': Store.query.count(),
                'total_products': Product.query.count(),
                'total_services': Service.query.count(),
                'total_orders': Order.query.count(),
                'pending_orders': Order.query.filter_by(status='pending').count(),
                'total_revenue': db.session.query(func.sum(Order.total_price)).filter_by(
                    status='delivered'
                ).scalar() or 0
            }
        except Exception as e:
            return {'error': f'فشل في جلب الإحصائيات: {str(e)}'}

# Create global instance
local_api_client = LocalAPIClient()