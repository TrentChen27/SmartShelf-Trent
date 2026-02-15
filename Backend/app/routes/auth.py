from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.account import OnlineAccount
from app.models.customer import Customer, Home, Business
from app.models.employee import Employee
from app.models.salesperson import SalesPerson
from app.models.address import Address

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/register', methods=['POST'])
def register():
    """Register a new customer"""
    data = request.get_json()

    # Validate required fields
    if not data.get('email') or not data.get('passwd') or not data.get('name'):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if email already exists
    if OnlineAccount.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    try:
        # Create online account
        account = OnlineAccount(
            email=data['email'],
            name=data['name']
        )
        account.set_password(data['passwd'])
        db.session.add(account)
        db.session.flush()

        # Create customer
        customer = Customer(
            online_id=account.online_id,
            kind=data.get('kind', 0)  # 0=home, 1=business
        )
        db.session.add(customer)
        db.session.flush()

        # Create Home or Business customer profile
        if customer.kind == 0:
            # Home customer
            home = Home(
                id=customer.id,
                gender=data.get('gender'),
                age=data.get('age'),
                marriage_status=data.get('marriage_status'),
                income=data.get('income')
            )
            db.session.add(home)
        else:
            # Business customer
            business = Business(
                id=customer.id,
                company_name=data.get('company_name'),
                category=data.get('category'),
                gross_income=data.get('gross_income')
            )
            db.session.add(business)

        db.session.commit()

        return jsonify({
            'message': 'Registration successful',
            'user': account.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """Login endpoint"""
    data = request.get_json()

    if not data.get('email') or not data.get('passwd'):
        return jsonify({'error': 'Missing email or password'}), 400

    # Find account
    account = OnlineAccount.query.filter_by(email=data['email']).first()

    if not account or not account.check_password(data['passwd']):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Determine user role
    role = 'customer'  # default
    user_data = account.to_dict()

    # Check if employee
    employee = Employee.query.filter_by(online_id=account.online_id).first()
    if employee:
        # Check if salesperson
        salesperson = SalesPerson.query.filter_by(employee_id=employee.id).first()
        if salesperson:
            role = 'sales'
            user_data['employee_id'] = employee.id
            user_data['store_id'] = salesperson.store_id
        # Check if manager (you'll need to implement this logic)
        elif employee.job_title == 'Store Manager':
            role = 'manager'
            user_data['employee_id'] = employee.id
        elif employee.job_title == 'Region Manager':
            role = 'region'
            user_data['employee_id'] = employee.id

    # Check if customer
    customer = Customer.query.filter_by(online_id=account.online_id).first()
    if customer:
        role = 'customer'
        user_data['customer_id'] = customer.id

    # Create JWT token (identity must be a string)
    token = create_access_token(
        identity=str(account.online_id),
        additional_claims={'role': role}
    )

    return jsonify({
        'token': token,
        'user': user_data,
        'role': role
    }), 200


@bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    """Get current user info"""
    online_id = int(get_jwt_identity())
    account = OnlineAccount.query.get(online_id)

    if not account:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(account.to_dict()), 200


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout endpoint (JWT is stateless, so this is mainly for client-side)"""
    return jsonify({'message': 'Logged out successfully'}), 200


@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's complete profile"""
    online_id = int(get_jwt_identity())

    account = OnlineAccount.query.get(online_id)
    if not account:
        return jsonify({'error': 'User not found'}), 404
    
    profile = account.to_dict()
    
    # Get customer info
    customer = Customer.query.filter_by(online_id=online_id).first()
    if customer:
        profile['customer'] = customer.to_dict()

        # Get address information
        if customer.address_id:
            address = Address.query.get(customer.address_id)
            if address:
                profile['customer']['address'] = address.to_dict()

        # Get Home or Business details
        sales_id = None
        if customer.kind == 0:
            home = Home.query.get(customer.id)
            if home:
                profile['customer_details'] = home.to_dict()
                sales_id = home.sales_id
        else:
            business = Business.query.get(customer.id)
            if business:
                profile['customer_details'] = business.to_dict()
                sales_id = business.sales_id

        # Get assigned salesperson info if exists
        if sales_id:
            salesperson = SalesPerson.query.filter_by(employee_id=sales_id).first()
            if salesperson:
                sales_employee = Employee.query.get(sales_id)
                if sales_employee:
                    sales_account = OnlineAccount.query.get(sales_employee.online_id)
                    # Get store information
                    from app.models.store import Store
                    store = Store.query.get(salesperson.store_id)
                    profile['assigned_sales'] = {
                        'employee_id': sales_employee.id,
                        'name': sales_account.name if sales_account else 'Unknown',
                        'email': sales_account.email if sales_account else 'N/A',
                        'store_id': salesperson.store_id,
                        'store_name': store.name if store else 'Unknown Store'
                    }
    
    # Get employee info
    employee = Employee.query.filter_by(online_id=online_id).first()
    if employee:
        profile['employee'] = employee.to_dict()

        from app.models.store import Store
        from app.models.region import Region

        # Try to find store association
        store = None

        # First check if they are a salesperson
        salesperson = SalesPerson.query.filter_by(employee_id=employee.id).first()
        if salesperson:
            profile['salesperson'] = salesperson.to_dict()
            store = Store.query.get(salesperson.store_id)
        else:
            # Check if they are a store manager
            store = Store.query.filter_by(manager_id=employee.id).first()

        # If we found a store (either as salesperson or manager), add store info
        if store:
            profile['store_info'] = {
                'id': store.id,
                'name': store.name,
                'address_id': store.address_id
            }

            # Get store manager info (if not the same person)
            if store.manager_id and store.manager_id != employee.id:
                manager_employee = Employee.query.get(store.manager_id)
                if manager_employee:
                    manager_account = OnlineAccount.query.get(manager_employee.online_id)
                    profile['store_manager'] = {
                        'employee_id': manager_employee.id,
                        'name': manager_account.name if manager_account else 'Unknown',
                        'email': manager_account.email if manager_account else 'N/A'
                    }
            elif store.manager_id == employee.id:
                # User is the store manager, also add the reference for comparison
                profile['store_manager'] = {
                    'employee_id': employee.id,
                    'name': account.name,
                    'email': account.email
                }

            # Get region manager info
            if store.region_id:
                region = Region.query.get(store.region_id)
                if region and region.region_manager:
                    region_manager_employee = Employee.query.get(region.region_manager)
                    if region_manager_employee:
                        region_manager_account = OnlineAccount.query.get(region_manager_employee.online_id)
                        profile['region_manager'] = {
                            'employee_id': region_manager_employee.id,
                            'name': region_manager_account.name if region_manager_account else 'Unknown',
                            'email': region_manager_account.email if region_manager_account else 'N/A',
                            'region_name': region.region_name
                        }

        # Check if this employee is a regional manager
        region = Region.query.filter_by(region_manager=employee.id).first()
        if region:
            profile['region_info'] = {
                'id': region.id,
                'region_name': region.region_name
            }

    return jsonify(profile), 200


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
    online_id = int(get_jwt_identity())
    data = request.get_json()

    account = OnlineAccount.query.get(online_id)
    if not account:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        # Check if user is an employee
        employee = Employee.query.filter_by(online_id=online_id).first()
        is_employee = employee is not None

        # Update account info
        if 'name' in data:
            # Employees cannot change their name (must contact HR)
            if is_employee:
                return jsonify({'error': 'Employees cannot change their name. Please contact HR.'}), 400
            account.name = data['name']

        if 'email' in data:
            # Employees cannot change their email (must contact IT)
            if is_employee:
                return jsonify({'error': 'Employees cannot change their email. Please contact IT.'}), 400
            # Check if email is already taken
            existing = OnlineAccount.query.filter_by(email=data['email']).first()
            if existing and existing.online_id != online_id:
                return jsonify({'error': 'Email already in use'}), 400
            account.email = data['email']
        
        # Update password if provided - require current password verification
        if 'passwd' in data and data['passwd']:
            # Must provide current password when changing password
            if 'current_password' not in data or not data['current_password']:
                return jsonify({'error': 'Current password is required to change password'}), 400
            
            # Verify current password
            if not account.check_password(data['current_password']):
                return jsonify({'error': 'Current password is incorrect'}), 401
            
            # Set new password
            account.set_password(data['passwd'])
        
        # Update customer details
        customer = Customer.query.filter_by(online_id=online_id).first()
        if customer:
            if customer.kind == 0:
                # Update Home customer
                home = Home.query.get(customer.id)
                if home:
                    if 'gender' in data:
                        home.gender = data['gender']
                    if 'age' in data:
                        home.age = data['age']
                    if 'marriage_status' in data:
                        home.marriage_status = data['marriage_status']
                    if 'income' in data:
                        home.income = data['income']
            else:
                # Update Business customer
                business = Business.query.get(customer.id)
                if business:
                    if 'company_name' in data:
                        business.company_name = data['company_name']
                    if 'category' in data:
                        business.category = data['category']
                    if 'gross_income' in data:
                        business.gross_income = data['gross_income']
        
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Profile update error: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500
