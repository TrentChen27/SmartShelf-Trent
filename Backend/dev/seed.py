"""
SmartShelf Database Seed Script
================================
Single unified script that:
1. Drops and recreates all tables
2. Seeds comprehensive test data
3. Includes regions, stores, employees, products, customers, inventory, and orders

Usage:
    python dev/seed.py

Requirements:
    - .env file with DATABASE_URL configured
"""
import psycopg2
from dotenv import load_dotenv
import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

def main():
    """Main seeding function"""
    
    # Check if DATABASE_URL is configured
    if not os.getenv('DATABASE_URL'):
        print("❌ Error: DATABASE_URL not found in .env file")
        sys.exit(1)
    
    # Connect to database
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)
    
    try:
        print("=" * 60)
        print("🌱 SmartShelf Database Seeding")
        print("=" * 60)
        
        # ============================================
        # STEP 1: Drop and recreate all tables
        # ============================================
        print("\n🗑️  STEP 1: Dropping existing tables...")
        try:
            cur.execute("""
                DROP TABLE IF EXISTS 
                    pickuprecord, 
                    orderitem, 
                    orders, 
                    storeinventory, 
                    business, 
                    home, 
                    salesperson, 
                    store, 
                    customer, 
                    employee, 
                    onlineaccount, 
                    product, 
                    region, 
                    address 
                CASCADE
            """)
            conn.commit()
            print("✅ All tables dropped")
        except Exception as e:
            print(f"⚠️  Warning: {e}")
            conn.rollback()
        
        # ============================================
        # STEP 2: Create tables from schema
        # ============================================
        print("\n🔨 STEP 2: Creating tables from schema...")
        try:
            # Read and execute the SQL schema file
            schema_path = os.path.join(os.path.dirname(__file__), '..', 'Table_postgres.sql')
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            cur.execute(schema_sql)
            conn.commit()
            print("✅ All tables created")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            conn.rollback()
            sys.exit(1)
        
        # ============================================
        # STEP 3: Create Regions
        # ============================================
        print("\n📍 STEP 3: Creating regions...")
        regions = [
            ('West Coast Region',),
            ('East Coast Region',),
            ('Central Region',)
        ]
        
        region_ids = []
        for region in regions:
            cur.execute("INSERT INTO region (region_name) VALUES (%s) RETURNING id", region)
            region_ids.append(cur.fetchone()[0])
        conn.commit()
        print(f"✅ Created {len(region_ids)} regions")
        
        # ============================================
        # STEP 4: Create Addresses
        # ============================================
        print("\n🏠 STEP 4: Creating addresses...")
        addresses = [
            # West Coast stores
            ('CA', 'San Francisco', 94102, '100 Market Street', 'Suite 200'),
            ('CA', 'Los Angeles', 90001, '200 Sunset Boulevard', None),
            ('WA', 'Seattle', 98101, '300 Pike Street', 'Floor 1'),
            
            # East Coast stores
            ('NY', 'New York', 10001, '400 Broadway', 'Suite 100'),
            ('MA', 'Boston', 2101, '500 Boylston Street', None),
            
            # Central stores
            ('IL', 'Chicago', 60601, '600 Michigan Avenue', None),
            ('TX', 'Dallas', 75201, '700 Main Street', 'Suite 300'),
        ]
        
        address_ids = []
        for addr in addresses:
            cur.execute(
                "INSERT INTO address (state, city, zipcode, address_1, address_2) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                addr
            )
            address_ids.append(cur.fetchone()[0])
        conn.commit()
        print(f"✅ Created {len(address_ids)} addresses")
        
        # ============================================
        # STEP 5: Create Online Accounts
        # ============================================
        print("\n👤 STEP 5: Creating online accounts...")
        
        # Password: password123 (hashed with pbkdf2:sha256)
        password_hash = generate_password_hash('password123', method='pbkdf2:sha256')
        
        accounts = [
            # Region Managers
            ('region.west@smartshelf.com', password_hash, 'Alice Johnson'),
            ('region.east@smartshelf.com', password_hash, 'Bob Williams'),
            ('region.central@smartshelf.com', password_hash, 'Carol Davis'),
            
            # Store Managers
            ('manager.sf@smartshelf.com', password_hash, 'David Chen'),
            ('manager.la@smartshelf.com', password_hash, 'Eva Martinez'),
            ('manager.seattle@smartshelf.com', password_hash, 'Frank Wilson'),
            ('manager.nyc@smartshelf.com', password_hash, 'Grace Lee'),
            ('manager.boston@smartshelf.com', password_hash, 'Henry Brown'),
            ('manager.chicago@smartshelf.com', password_hash, 'Iris Taylor'),
            ('manager.dallas@smartshelf.com', password_hash, 'Jack Anderson'),
            
            # Sales People
            ('sales.sf1@smartshelf.com', password_hash, 'Kate Miller'),
            ('sales.sf2@smartshelf.com', password_hash, 'Leo Garcia'),
            ('sales.la1@smartshelf.com', password_hash, 'Maria Rodriguez'),
            ('sales.la2@smartshelf.com', password_hash, 'Nathan White'),
            
            # Customers
            ('customer1@test.com', password_hash, 'John Smith'),
            ('customer2@test.com', password_hash, 'Sarah Johnson'),
            ('customer3@test.com', password_hash, 'Michael Brown'),
            ('business1@test.com', password_hash, 'TechCorp Inc'),
            ('business2@test.com', password_hash, 'StartupHub LLC'),
        ]
        
        account_ids = []
        for acc in accounts:
            cur.execute(
                "INSERT INTO onlineaccount (email, passwd, name) VALUES (%s, %s, %s) RETURNING online_id",
                acc
            )
            account_ids.append(cur.fetchone()[0])
        conn.commit()
        print(f"✅ Created {len(account_ids)} online accounts")
        
        # Map accounts
        region_manager_ids = account_ids[0:3]
        store_manager_ids = account_ids[3:10]
        sales_ids = account_ids[10:14]
        customer_ids = account_ids[14:]
        
        # ============================================
        # STEP 6: Create Employees
        # ============================================
        print("\n💼 STEP 6: Creating employees...")
        
        employees = []
        # Region Managers
        for acc_id in region_manager_ids:
            employees.append((acc_id, 'Region Manager', 120000))
        
        # Store Managers
        for acc_id in store_manager_ids:
            employees.append((acc_id, 'Store Manager', 80000))
        
        # Sales People
        for acc_id in sales_ids:
            employees.append((acc_id, 'Sales', 50000))
        
        employee_ids = []
        for emp in employees:
            cur.execute(
                "INSERT INTO employee (online_id, job_title, salary) VALUES (%s, %s, %s) RETURNING id",
                emp
            )
            employee_ids.append(cur.fetchone()[0])
        conn.commit()
        
        region_manager_emp_ids = employee_ids[0:3]
        store_manager_emp_ids = employee_ids[3:10]
        sales_emp_ids = employee_ids[10:14]
        
        print(f"✅ Created {len(employee_ids)} employees")
        
        # Update regions with managers
        for i, region_id in enumerate(region_ids):
            cur.execute(
                "UPDATE region SET region_manager = %s WHERE id = %s",
                (region_manager_emp_ids[i], region_id)
            )
        conn.commit()
        
        # ============================================
        # STEP 7: Create Stores
        # ============================================
        print("\n🏪 STEP 7: Creating stores...")
        
        stores = [
            # West Coast Region
            ('SF Downtown Store', address_ids[0], store_manager_emp_ids[0], region_ids[0]),
            ('LA Westside Store', address_ids[1], store_manager_emp_ids[1], region_ids[0]),
            ('Seattle Pike Place', address_ids[2], store_manager_emp_ids[2], region_ids[0]),
            
            # East Coast Region
            ('NYC Broadway Store', address_ids[3], store_manager_emp_ids[3], region_ids[1]),
            ('Boston Downtown', address_ids[4], store_manager_emp_ids[4], region_ids[1]),
            
            # Central Region
            ('Chicago Loop Store', address_ids[5], store_manager_emp_ids[5], region_ids[2]),
            ('Dallas Main Street', address_ids[6], store_manager_emp_ids[6], region_ids[2]),
        ]
        
        store_ids = []
        for store in stores:
            cur.execute(
                "INSERT INTO store (name, address_id, manager_id, region_id) VALUES (%s, %s, %s, %s) RETURNING id",
                store
            )
            store_ids.append(cur.fetchone()[0])
        conn.commit()
        print(f"✅ Created {len(store_ids)} stores")
        
        # ============================================
        # STEP 8: Create Sales People
        # ============================================
        print("\n👔 STEP 8: Assigning sales people to stores...")
        
        sales_assignments = [
            (store_ids[0], sales_emp_ids[0]),  # SF store
            (store_ids[0], sales_emp_ids[1]),  # SF store
            (store_ids[1], sales_emp_ids[2]),  # LA store
            (store_ids[1], sales_emp_ids[3]),  # LA store
        ]
        
        cur.executemany(
            "INSERT INTO salesperson (store_id, employee_id) VALUES (%s, %s)",
            sales_assignments
        )
        conn.commit()
        print(f"✅ Created {len(sales_assignments)} sales assignments")
        
        # ============================================
        # STEP 9: Create Customers
        # ============================================
        print("\n🛍️  STEP 9: Creating customers...")
        
        # Home customers (3)
        home_customers = []
        for i in range(3):
            cur.execute(
                "INSERT INTO customer (online_id, kind, address_id) VALUES (%s, %s, %s) RETURNING id",
                (customer_ids[i], 0, None)
            )
            customer_id = cur.fetchone()[0]
            home_customers.append(customer_id)
        
        # Home customer details
        home_details = [
            (home_customers[0], 1, 'Male', 35, 75000, sales_emp_ids[0]),    # Married
            (home_customers[1], 0, 'Female', 28, 65000, sales_emp_ids[1]),  # Single
            (home_customers[2], 1, 'Male', 42, 95000, sales_emp_ids[2]),    # Married
        ]
        
        cur.executemany(
            "INSERT INTO home (id, marriage_status, gender, age, income, sales_id) VALUES (%s, %s, %s, %s, %s, %s)",
            home_details
        )
        
        # Business customers (2)
        business_customers = []
        for i in range(2):
            cur.execute(
                "INSERT INTO customer (online_id, kind, address_id) VALUES (%s, %s, %s) RETURNING id",
                (customer_ids[3 + i], 1, None)
            )
            customer_id = cur.fetchone()[0]
            business_customers.append(customer_id)
        
        # Business customer details
        business_details = [
            (business_customers[0], 'TechCorp Inc', 'Technology', 5000000, sales_emp_ids[0]),
            (business_customers[1], 'StartupHub LLC', 'Startup', 1000000, sales_emp_ids[3]),
        ]
        
        cur.executemany(
            "INSERT INTO business (id, company_name, category, gross_income, sales_id) VALUES (%s, %s, %s, %s, %s)",
            business_details
        )
        
        conn.commit()
        print(f"✅ Created {len(home_customers)} home customers and {len(business_customers)} business customers")
        
        # ============================================
        # STEP 10: Create Products
        # ============================================
        print("\n📱 STEP 10: Creating products...")
        
        products = [
            # === PHONES ===
            (
                'Apple iPhone 15 Pro Max',
                119900,  # $1199.00
                'Phone',
                'Latest iPhone with A17 Pro chip, titanium design, 6.7-inch Super Retina XDR display, and advanced camera system with 5x optical zoom.',
                'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&auto=format&fit=crop'
            ),
            (
                'Apple iPhone 15',
                79900,  # $799.00
                'Phone',
                'All-new iPhone 15 with Dynamic Island, 48MP main camera, and USB-C. Available in stunning colors.',
                'https://images.unsplash.com/photo-1695653422715-991ec3a0db9a?w=800&auto=format&fit=crop'
            ),
            (
                'Samsung Galaxy S24 Ultra',
                119900,  # $1199.00
                'Phone',
                'Premium Android flagship with S Pen, AI-powered camera, Snapdragon 8 Gen 3, and stunning 6.8-inch Dynamic AMOLED display.',
                'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800&auto=format&fit=crop'
            ),
            (
                'Samsung Galaxy S24',
                79900,  # $799.00
                'Phone',
                'Compact flagship with AI features, excellent camera system, and smooth 120Hz display in a premium design.',
                'https://images.unsplash.com/photo-1672204611425-23684cb0b7c6?w=800&auto=format&fit=crop'
            ),
            (
                'Google Pixel 8 Pro',
                99900,  # $999.00
                'Phone',
                'Google\'s flagship with AI-powered photography, Tensor G3 chip, and pure Android experience with 7 years of updates.',
                'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&auto=format&fit=crop'
            ),
            (
                'Google Pixel 8',
                69900,  # $699.00
                'Phone',
                'Compact Pixel with excellent camera, Google AI features, and the smoothest Android experience.',
                'https://images.unsplash.com/photo-1687203302662-8532fdbd0eda?w=800&auto=format&fit=crop'
            ),
            
            # === TABLETS ===
            (
                'Apple iPad Pro 12.9-inch (M2)',
                109900,  # $1099.00
                'Tablet',
                'Ultimate iPad with M2 chip, stunning Liquid Retina XDR display, and support for Apple Pencil and Magic Keyboard.',
                'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&auto=format&fit=crop'
            ),
            (
                'Apple iPad Air (M2)',
                59900,  # $599.00
                'Tablet',
                'Powerful and versatile iPad with M2 chip, 10.9-inch Liquid Retina display, perfect for creativity and productivity.',
                'https://images.unsplash.com/photo-1561154464-82e9adf32764?w=800&auto=format&fit=crop'
            ),
            (
                'Apple iPad (10th Gen)',
                34900,  # $349.00
                'Tablet',
                'Colorful and capable iPad with A14 Bionic, 10.9-inch display, and all-day battery life.',
                'https://images.unsplash.com/photo-1585790050230-5dd28404ccb9?w=800&auto=format&fit=crop'
            ),
            (
                'Samsung Galaxy Tab S9 Ultra',
                119900,  # $1199.00
                'Tablet',
                'Premium Android tablet with massive 14.6-inch Dynamic AMOLED display, S Pen included, and desktop-class performance.',
                'https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800&auto=format&fit=crop'
            ),
            (
                'Samsung Galaxy Tab S9',
                79900,  # $799.00
                'Tablet',
                'High-performance tablet with 11-inch display, S Pen, and IP68 water resistance for work and play.',
                'https://images.unsplash.com/photo-1632833239869-a37e3a5806d2?w=800&auto=format&fit=crop'
            ),
            (
                'Microsoft Surface Pro 9',
                99900,  # $999.00
                'Tablet',
                'Versatile 2-in-1 with 12th Gen Intel processor, vibrant PixelSense display, and laptop-grade performance.',
                'https://images.unsplash.com/photo-1632441499376-501a1f43e710?w=800&auto=format&fit=crop'
            ),
            
            # === LAPTOPS ===
            (
                'Apple MacBook Pro 16-inch (M3 Pro)',
                249900,  # $2499.00
                'Laptop',
                'Powerhouse laptop with M3 Pro chip, stunning Liquid Retina XDR display, and up to 22 hours battery life.',
                'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop'
            ),
            (
                'Apple MacBook Pro 14-inch (M3)',
                159900,  # $1599.00
                'Laptop',
                'Pro laptop with M3 chip, brilliant display, and incredible performance in a compact design.',
                'https://images.unsplash.com/photo-1629131726692-1accd0c53ce0?w=800&auto=format&fit=crop'
            ),
            (
                'Apple MacBook Air 15-inch (M3)',
                129900,  # $1299.00
                'Laptop',
                'Spacious 15-inch display with M3 chip, fanless design, and up to 18 hours of battery life.',
                'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800&auto=format&fit=crop'
            ),
            (
                'Apple MacBook Air 13-inch (M3)',
                109900,  # $1099.00
                'Laptop',
                'Incredibly portable with M3 chip, brilliant Retina display, and all-day battery in a stunning design.',
                'https://images.unsplash.com/photo-1606229365485-93a3b8ee0385?w=800&auto=format&fit=crop'
            ),
            (
                'Dell XPS 15 (2024)',
                179900,  # $1799.00
                'Laptop',
                'Premium Windows laptop with Intel Core Ultra 7, NVIDIA RTX 4050, and stunning OLED display.',
                'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&auto=format&fit=crop'
            ),
            (
                'Dell XPS 13 Plus',
                129900,  # $1299.00
                'Laptop',
                'Ultra-modern design with Intel Core Ultra, edge-to-edge keyboard, and stunning 13.4-inch display.',
                'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop'
            ),
            (
                'HP Spectre x360 14',
                149900,  # $1499.00
                'Laptop',
                'Convertible 2-in-1 with Intel Core Ultra, stunning OLED display, and premium gem-cut design.',
                'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&auto=format&fit=crop'
            ),
            (
                'Lenovo ThinkPad X1 Carbon Gen 11',
                159900,  # $1599.00
                'Laptop',
                'Business ultrabook with Intel Core Ultra, legendary keyboard, and military-grade durability.',
                'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop'
            ),
            (
                'Microsoft Surface Laptop 5',
                129900,  # $1299.00
                'Laptop',
                'Sleek Windows laptop with 12th Gen Intel processor, PixelSense touchscreen, and premium Alcantara keyboard.',
                'https://images.unsplash.com/photo-1624705002806-5d72df19c3ad?w=800&auto=format&fit=crop'
            ),
        ]
        
        product_ids = []
        for prod in products:
            cur.execute(
                "INSERT INTO product (product_name, price, kind, description, image_url) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                prod
            )
            product_ids.append(cur.fetchone()[0])
        conn.commit()
        print(f"✅ Created {len(product_ids)} products")
        
        # ============================================
        # STEP 11: Create Store Inventory
        # ============================================
        print("\n📦 STEP 11: Creating store inventory...")
        
        # Stock products in SF and LA stores
        target_stores = [store_ids[0], store_ids[1]]  # SF and LA
        
        inventory = []
        for store_id in target_stores:
            for i, product_id in enumerate(product_ids):
                # Varying stock levels: phones (20-50), tablets (15-35), laptops (10-25)
                kind_index = i // 6  # 0=phones, 1=tablets, 2=laptops
                if kind_index == 0:  # Phones
                    base_stock = 30
                    variance = 20
                elif kind_index == 1:  # Tablets
                    base_stock = 20
                    variance = 15
                else:  # Laptops
                    base_stock = 15
                    variance = 10
                
                stock = base_stock + ((product_id * store_id) % variance)
                inventory.append((store_id, product_id, stock))
        
        cur.executemany(
            "INSERT INTO storeinventory (store_id, product_id, stock) VALUES (%s, %s, %s)",
            inventory
        )
        conn.commit()
        print(f"✅ Created {len(inventory)} inventory items")
        
        # ============================================
        # STEP 12: Create Orders for customer1@test.com
        # ============================================
        print("\n📋 STEP 12: Creating sample orders...")
        
        # Get customer1's ID
        customer1_id = home_customers[0]
        
        # Create 6 orders with different states
        orders_data = []
        order_items_data = []
        
        # Order 1: Paid, Pending Pickup (recent)
        order_date_1 = datetime.now() - timedelta(days=1)
        order_1_items = [
            (product_ids[0], 1, product_ids[0] * 119900),  # iPhone 15 Pro Max
            (product_ids[7], 1, product_ids[7] * 59900),   # iPad Air
        ]
        order_1_total = sum(item[2] for item in order_1_items)
        orders_data.append((customer1_id, store_ids[0], sales_emp_ids[0], order_date_1, order_1_total, True, 0))
        
        # Order 2: Paid, Picked Up (3 days ago)
        order_date_2 = datetime.now() - timedelta(days=3)
        order_2_items = [
            (product_ids[4], 1, product_ids[4] * 99900),   # Google Pixel 8 Pro
        ]
        order_2_total = sum(item[2] for item in order_2_items)
        orders_data.append((customer1_id, store_ids[1], sales_emp_ids[2], order_date_2, order_2_total, True, 1))
        
        # Order 3: Unpaid, Pending Pickup (2 days ago)
        order_date_3 = datetime.now() - timedelta(days=2)
        order_3_items = [
            (product_ids[11], 1, product_ids[11] * 99900),  # Surface Pro 9
            (product_ids[2], 1, product_ids[2] * 119900),   # Galaxy S24 Ultra
        ]
        order_3_total = sum(item[2] for item in order_3_items)
        orders_data.append((customer1_id, store_ids[0], sales_emp_ids[1], order_date_3, order_3_total, False, 0))
        
        # Order 4: Paid, Cancelled (5 days ago)
        order_date_4 = datetime.now() - timedelta(days=5)
        order_4_items = [
            (product_ids[13], 1, product_ids[13] * 159900),  # MacBook Pro 14
        ]
        order_4_total = sum(item[2] for item in order_4_items)
        orders_data.append((customer1_id, store_ids[1], sales_emp_ids[3], order_date_4, order_4_total, True, 2))
        
        # Order 5: Paid, Picked Up (7 days ago)
        order_date_5 = datetime.now() - timedelta(days=7)
        order_5_items = [
            (product_ids[1], 2, 2 * product_ids[1] * 79900),   # iPhone 15 x2
            (product_ids[8], 1, product_ids[8] * 34900),       # iPad 10th Gen
        ]
        order_5_total = sum(item[2] for item in order_5_items)
        orders_data.append((customer1_id, store_ids[0], sales_emp_ids[0], order_date_5, order_5_total, True, 1))
        
        # Order 6: Paid, Pending Pickup (today)
        order_date_6 = datetime.now()
        order_6_items = [
            (product_ids[16], 1, product_ids[16] * 179900),  # Dell XPS 15
        ]
        order_6_total = sum(item[2] for item in order_6_items)
        orders_data.append((customer1_id, store_ids[1], sales_emp_ids[2], order_date_6, order_6_total, True, 0))
        
        # Insert orders
        order_ids = []
        for order in orders_data:
            cur.execute(
                "INSERT INTO orders (customer_id, store_id, sales_id, order_date, total_amount, payment_status, pickup_status) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                order
            )
            order_ids.append(cur.fetchone()[0])
        
        # Prepare order items with order_id
        all_order_items = [
            order_1_items,
            order_2_items,
            order_3_items,
            order_4_items,
            order_5_items,
            order_6_items
        ]
        
        for i, order_id in enumerate(order_ids):
            for product_id, quantity, sub_price in all_order_items[i]:
                cur.execute(
                    "INSERT INTO orderitem (order_id, product_id, quantity, sub_price) VALUES (%s, %s, %s, %s)",
                    (order_id, product_id, quantity, sub_price)
                )
        
        conn.commit()
        print(f"✅ Created {len(order_ids)} orders for customer1@test.com")
        
        # ============================================
        # SUCCESS SUMMARY
        # ============================================
        print("\n" + "=" * 60)
        print("🎉 DATABASE SEEDED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\n📊 Summary:")
        print(f"  • {len(region_ids)} Regions")
        print(f"  • {len(store_ids)} Stores")
        print(f"  • {len(employee_ids)} Employees ({len(region_manager_emp_ids)} managers, {len(store_manager_emp_ids)} store managers, {len(sales_emp_ids)} sales)")
        print(f"  • {len(product_ids)} Products")
        print(f"  • {len(inventory)} Inventory items")
        print(f"  • {len(home_customers)} Home customers + {len(business_customers)} Business customers")
        print(f"  • {len(order_ids)} Orders")
        
        print("\n🔑 Test Accounts (password: password123):")
        print("\n  👥 Customers:")
        print("    • customer1@test.com - John Smith (Home)")
        print("    • customer2@test.com - Sarah Johnson (Home)")
        print("    • customer3@test.com - Michael Brown (Home)")
        print("    • business1@test.com - TechCorp Inc (Business)")
        print("    • business2@test.com - StartupHub LLC (Business)")
        
        print("\n  👔 Sales People:")
        print("    • sales.sf1@smartshelf.com - Kate Miller")
        print("    • sales.sf2@smartshelf.com - Leo Garcia")
        print("    • sales.la1@smartshelf.com - Maria Rodriguez")
        print("    • sales.la2@smartshelf.com - Nathan White")
        
        print("\n  🏪 Store Managers:")
        print("    • manager.sf@smartshelf.com - David Chen")
        print("    • manager.la@smartshelf.com - Eva Martinez")
        print("    • manager.seattle@smartshelf.com - Frank Wilson")
        print("    • manager.nyc@smartshelf.com - Grace Lee")
        
        print("\n  🌍 Region Managers:")
        print("    • region.west@smartshelf.com - Alice Johnson")
        print("    • region.east@smartshelf.com - Bob Williams")
        print("    • region.central@smartshelf.com - Carol Davis")
        
        print("\n🏪 Stores:")
        print("    • SF Downtown Store (San Francisco, CA) ✅ Has inventory")
        print("    • LA Westside Store (Los Angeles, CA) ✅ Has inventory")
        print("    • Seattle Pike Place (Seattle, WA)")
        print("    • NYC Broadway Store (New York, NY)")
        print("    • Boston Downtown (Boston, MA)")
        print("    • Chicago Loop Store (Chicago, IL)")
        print("    • Dallas Main Street (Dallas, TX)")
        
        print("\n📱 Products:")
        print("    • 6 Phones (iPhone, Samsung, Google Pixel)")
        print("    • 6 Tablets (iPad, Galaxy Tab, Surface)")
        print("    • 9 Laptops (MacBook, Dell, HP, Lenovo, Surface)")
        
        print("\n✨ Ready to use! You can now:")
        print("    1. Start the backend: cd Backend && python run.py")
        print("    2. Start the frontend: cd Frontend && npm run dev")
        print("    3. Login with any test account above")
        print("    4. Browse products and test features")
        
        print("=" * 60)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
