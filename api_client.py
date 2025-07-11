import requests
import os
import logging
from typing import Dict, List, Optional, Any

class APIClient:
    """Client for communicating with the existing BaytAlSudani API"""
    
    def __init__(self):
        self.base_url = os.environ.get('API_BASE_URL', 'http://localhost:8000/api')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make HTTP request to API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {'error': 'البيانات غير موجودة', 'status_code': 404}
            elif response.status_code == 401:
                return {'error': 'غير مصرح بالوصول', 'status_code': 401}
            else:
                return {'error': f'خطأ في الخادم: {response.status_code}', 'status_code': response.status_code}
                
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            return {'error': 'فشل في الاتصال بالخادم', 'exception': str(e)}
    
    # Authentication methods
    def login_admin(self, username: str, password: str) -> Dict:
        """Admin login"""
        return self._make_request('POST', '/auth/admin/login', {
            'username': username,
            'password': password
        })
    
    def login_merchant(self, email: str, password: str) -> Dict:
        """Merchant login"""
        return self._make_request('POST', '/auth/merchant/login', {
            'email': email,
            'password': password
        })
    
    # User management methods
    def get_users(self, page: int = 1, limit: int = 20) -> Dict:
        """Get all users"""
        return self._make_request('GET', '/users', params={'page': page, 'limit': limit})
    
    def get_user(self, user_id: int) -> Dict:
        """Get user by ID"""
        return self._make_request('GET', f'/users/{user_id}')
    
    def update_user(self, user_id: int, data: Dict) -> Dict:
        """Update user"""
        return self._make_request('PUT', f'/users/{user_id}', data)
    
    def delete_user(self, user_id: int) -> Dict:
        """Delete user"""
        return self._make_request('DELETE', f'/users/{user_id}')
    
    def toggle_user_status(self, user_id: int) -> Dict:
        """Toggle user active status"""
        return self._make_request('POST', f'/users/{user_id}/toggle-status')
    
    # Store management methods
    def get_stores(self, page: int = 1, limit: int = 20) -> Dict:
        """Get all stores"""
        return self._make_request('GET', '/stores', params={'page': page, 'limit': limit})
    
    def get_store(self, store_id: int) -> Dict:
        """Get store by ID"""
        return self._make_request('GET', f'/stores/{store_id}')
    
    def update_store(self, store_id: int, data: Dict) -> Dict:
        """Update store"""
        return self._make_request('PUT', f'/stores/{store_id}', data)
    
    def delete_store(self, store_id: int) -> Dict:
        """Delete store"""
        return self._make_request('DELETE', f'/stores/{store_id}')
    
    def get_merchant_store(self, merchant_id: int) -> Dict:
        """Get store by merchant ID"""
        return self._make_request('GET', f'/merchants/{merchant_id}/store')
    
    # Product management methods
    def get_products(self, page: int = 1, limit: int = 20, store_id: Optional[int] = None) -> Dict:
        """Get products"""
        params = {'page': page, 'limit': limit}
        if store_id:
            params['store_id'] = store_id
        return self._make_request('GET', '/products', params=params)
    
    def get_product(self, product_id: int) -> Dict:
        """Get product by ID"""
        return self._make_request('GET', f'/products/{product_id}')
    
    def create_product(self, data: Dict) -> Dict:
        """Create new product"""
        return self._make_request('POST', '/products', data)
    
    def update_product(self, product_id: int, data: Dict) -> Dict:
        """Update product"""
        return self._make_request('PUT', f'/products/{product_id}', data)
    
    def delete_product(self, product_id: int) -> Dict:
        """Delete product"""
        return self._make_request('DELETE', f'/products/{product_id}')
    
    # Service management methods
    def get_services(self, page: int = 1, limit: int = 20, store_id: Optional[int] = None) -> Dict:
        """Get services"""
        params = {'page': page, 'limit': limit}
        if store_id:
            params['store_id'] = store_id
        return self._make_request('GET', '/services', params=params)
    
    def get_service(self, service_id: int) -> Dict:
        """Get service by ID"""
        return self._make_request('GET', f'/services/{service_id}')
    
    def create_service(self, data: Dict) -> Dict:
        """Create new service"""
        return self._make_request('POST', '/services', data)
    
    def update_service(self, service_id: int, data: Dict) -> Dict:
        """Update service"""
        return self._make_request('PUT', f'/services/{service_id}', data)
    
    def delete_service(self, service_id: int) -> Dict:
        """Delete service"""
        return self._make_request('DELETE', f'/services/{service_id}')
    
    # Job management methods
    def get_jobs(self, page: int = 1, limit: int = 20) -> Dict:
        """Get jobs"""
        return self._make_request('GET', '/jobs', params={'page': page, 'limit': limit})
    
    def get_job(self, job_id: int) -> Dict:
        """Get job by ID"""
        return self._make_request('GET', f'/jobs/{job_id}')
    
    def update_job(self, job_id: int, data: Dict) -> Dict:
        """Update job"""
        return self._make_request('PUT', f'/jobs/{job_id}', data)
    
    def delete_job(self, job_id: int) -> Dict:
        """Delete job"""
        return self._make_request('DELETE', f'/jobs/{job_id}')
    
    # Advertisement management methods
    def get_ads(self, page: int = 1, limit: int = 20) -> Dict:
        """Get advertisements"""
        return self._make_request('GET', '/ads', params={'page': page, 'limit': limit})
    
    def get_ad(self, ad_id: int) -> Dict:
        """Get advertisement by ID"""
        return self._make_request('GET', f'/ads/{ad_id}')
    
    def update_ad(self, ad_id: int, data: Dict) -> Dict:
        """Update advertisement"""
        return self._make_request('PUT', f'/ads/{ad_id}', data)
    
    def delete_ad(self, ad_id: int) -> Dict:
        """Delete advertisement"""
        return self._make_request('DELETE', f'/ads/{ad_id}')
    
    # Statistics methods
    def get_stats(self) -> Dict:
        """Get dashboard statistics"""
        return self._make_request('GET', '/stats')
    
    # Order management methods
    def get_orders(self, store_id: Optional[int] = None, page: int = 1, limit: int = 20) -> Dict:
        """Get orders"""
        params = {'page': page, 'limit': limit}
        if store_id:
            params['store_id'] = store_id
        return self._make_request('GET', '/orders', params=params)
    
    def get_order(self, order_id: int) -> Dict:
        """Get order by ID"""
        return self._make_request('GET', f'/orders/{order_id}')
    
    def update_order_status(self, order_id: int, status: str) -> Dict:
        """Update order status"""
        return self._make_request('PUT', f'/orders/{order_id}/status', {'status': status})
    
    # Subscription management methods
    def get_subscription(self, merchant_id: int) -> Dict:
        """Get merchant subscription"""
        return self._make_request('GET', f'/subscriptions/{merchant_id}')
    
    def get_subscription_history(self, merchant_id: int) -> Dict:
        """Get subscription history"""
        return self._make_request('GET', f'/subscriptions/{merchant_id}/history')

# Global API client instance
api_client = APIClient()
