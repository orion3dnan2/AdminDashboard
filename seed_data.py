"""
Seed data script for BaytAlSudani Admin Dashboard
Creates sample data for testing and demonstration
"""
from app import app
from models import db, User, Store, Product, Service, Order, Advertisement, Job
from auth import create_merchant_user
from decimal import Decimal

def create_sample_data():
    """Create sample data for testing"""
    with app.app_context():
        print("Creating sample data...")
        
        # Create sample merchants
        merchants_data = [
            ('ahmed_store', 'ahmed@example.com', 'password123'),
            ('fatima_shop', 'fatima@example.com', 'password123'),
            ('omar_market', 'omar@example.com', 'password123'),
        ]
        
        for username, email, password in merchants_data:
            existing_merchant = User.query.filter_by(username=username).first()
            if not existing_merchant:
                merchant, error = create_merchant_user(username, email, password)
                if merchant:
                    print(f"Created merchant: {username}")
                    
                    # Create store for merchant
                    store = Store(
                        name=f"متجر {username}",
                        description=f"متجر متخصص في بيع المنتجات المحلية",
                        merchant_id=merchant.id
                    )
                    db.session.add(store)
                    db.session.commit()
                    
                    # Create products for store
                    products_data = [
                        (f"منتج أ من {username}", "منتج عالي الجودة", 25.50),
                        (f"منتج ب من {username}", "منتج مميز بسعر منافس", 45.75),
                        (f"منتج ج من {username}", "منتج جديد ومبتكر", 30.00),
                    ]
                    
                    for name, desc, price in products_data:
                        product = Product(
                            name=name,
                            description=desc,
                            price=Decimal(str(price)),
                            merchant_id=merchant.id,
                            store_id=store.id
                        )
                        db.session.add(product)
                    
                    # Create services for store
                    services_data = [
                        (f"خدمة التوصيل من {username}", "خدمة توصيل سريعة ومضمونة", 10.00),
                        (f"خدمة الصيانة من {username}", "خدمة صيانة احترافية", 50.00),
                    ]
                    
                    for name, desc, price in services_data:
                        service = Service(
                            name=name,
                            description=desc,
                            price=Decimal(str(price)),
                            store_id=store.id
                        )
                        db.session.add(service)
                    
                    db.session.commit()
                    
                    # Create sample orders
                    products = Product.query.filter_by(store_id=store.id).all()
                    for i, product in enumerate(products[:2]):  # Only first 2 products
                        order = Order(
                            product_id=product.id,
                            quantity=2,
                            total_price=product.price * 2,
                            status='pending' if i == 0 else 'confirmed',
                            merchant_id=merchant.id,
                            customer_name=f"عميل تجريبي {i+1}",
                            customer_phone=f"0123456789{i}",
                            customer_address=f"عنوان تجريبي {i+1}, الخرطوم"
                        )
                        db.session.add(order)
                    
                    db.session.commit()
                    print(f"Created store, products, services and orders for {username}")
                else:
                    print(f"Failed to create merchant {username}: {error}")
        
        # Create sample advertisements
        ads_data = [
            ("إعلان تجريبي 1", "هذا إعلان تجريبي للمنصة"),
            ("عروض خاصة", "تسوق الآن واحصل على خصومات مميزة"),
            ("منتجات جديدة", "اكتشف أحدث المنتجات في المنصة"),
        ]
        
        for title, desc in ads_data:
            existing_ad = Advertisement.query.filter_by(title=title).first()
            if not existing_ad:
                ad = Advertisement(title=title, description=desc)
                db.session.add(ad)
        
        # Create sample jobs
        jobs_data = [
            ("مطور ويب", "مطلوب مطور ويب خبرة 3 سنوات", "شركة التقنية", "الخرطوم", "2000-4000 جنيه"),
            ("مصمم جرافيك", "مطلوب مصمم جرافيك محترف", "وكالة الإبداع", "أم درمان", "1500-3000 جنيه"),
            ("محاسب", "مطلوب محاسب خبرة في النظم المالية", "شركة المحاسبة", "بحري", "2500-5000 جنيه"),
        ]
        
        for title, desc, company, location, salary in jobs_data:
            existing_job = Job.query.filter_by(title=title, company=company).first()
            if not existing_job:
                job = Job(
                    title=title,
                    description=desc,
                    company=company,
                    location=location,
                    salary=salary
                )
                db.session.add(job)
        
        db.session.commit()
        print("Sample data created successfully!")
        
        # Print summary
        print("\n=== Summary ===")
        print(f"Total users: {User.query.count()}")
        print(f"Merchants: {User.query.filter_by(role='merchant').count()}")
        print(f"Admins: {User.query.filter_by(role='admin').count()}")
        print(f"Stores: {Store.query.count()}")
        print(f"Products: {Product.query.count()}")
        print(f"Services: {Service.query.count()}")
        print(f"Orders: {Order.query.count()}")
        print(f"Advertisements: {Advertisement.query.count()}")
        print(f"Jobs: {Job.query.count()}")

if __name__ == '__main__':
    create_sample_data()