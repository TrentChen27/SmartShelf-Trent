from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.customer import Customer, Home, Business
from app.models.account import OnlineAccount
from app.models.salesperson import SalesPerson
from app.models.employee import Employee
from app.models.order import Orders
from app.models.address import Address
from sqlalchemy import func

bp = Blueprint('customers', __name__, url_prefix='/api/customers')


@bp.route('', methods=['GET'])
@jwt_required()
def get_customers():
    """Get customers list (for sales, manager, region roles)"""
    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    # Only sales, manager, and region can view customers
    if role not in ['sales', 'manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get query parameters
    search = request.args.get('search', '')
    kind = request.args.get('kind', type=int)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    # Limit maximum page size
    limit = min(limit, 100)

    # Build query
    query = Customer.query

    # Filter by customer type if specified
    if kind is not None:
        query = query.filter_by(kind=kind)

    # Role-based filtering
    if role == 'sales':
        # Sales can only see their own customers
        employee = Employee.query.filter_by(online_id=online_id).first()
        if employee:
            salesperson = SalesPerson.query.filter_by(employee_id=employee.id).first()
            if salesperson:
                # Get customers assigned to this salesperson
                if kind == 0 or kind is None:
                    home_customers = Home.query.filter_by(sales_id=salesperson.employee_id).all()
                    home_customer_ids = [h.id for h in home_customers]
                else:
                    home_customer_ids = []

                if kind == 1 or kind is None:
                    business_customers = Business.query.filter_by(sales_id=salesperson.employee_id).all()
                    business_customer_ids = [b.id for b in business_customers]
                else:
                    business_customer_ids = []

                customer_ids = home_customer_ids + business_customer_ids
                if customer_ids:
                    query = query.filter(Customer.id.in_(customer_ids))
                else:
                    # No customers for this salesperson
                    return jsonify({'customers': [], 'total': 0, 'page': page, 'limit': limit}), 200

    elif role == 'manager':
        # Manager can see customers from their store
        employee = Employee.query.filter_by(online_id=online_id).first()
        if employee:
            salesperson = SalesPerson.query.filter_by(employee_id=employee.id).first()
            if salesperson:
                store_id = salesperson.store_id
                # Get all salespeople from this store
                store_salespeople = SalesPerson.query.filter_by(store_id=store_id).all()
                salesperson_ids = [sp.employee_id for sp in store_salespeople]

                if kind == 0 or kind is None:
                    home_customers = Home.query.filter(Home.sales_id.in_(salesperson_ids)).all()
                    home_customer_ids = [h.id for h in home_customers]
                else:
                    home_customer_ids = []

                if kind == 1 or kind is None:
                    business_customers = Business.query.filter(Business.sales_id.in_(salesperson_ids)).all()
                    business_customer_ids = [b.id for b in business_customers]
                else:
                    business_customer_ids = []

                customer_ids = home_customer_ids + business_customer_ids
                if customer_ids:
                    query = query.filter(Customer.id.in_(customer_ids))
                else:
                    return jsonify({'customers': [], 'total': 0, 'page': page, 'limit': limit}), 200

    # Region managers can see all customers (no additional filter needed)

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    customers_list = query.offset(offset).limit(limit).all()

    # Build response with customer details
    result = []
    for customer in customers_list:
        # Get account info
        account = OnlineAccount.query.get(customer.online_id)
        if not account:
            continue

        customer_data = {
            'id': customer.id,
            'online_id': customer.online_id,
            'name': account.name,
            'email': account.email,
            'kind': customer.kind
        }

        # Get address information
        if customer.address_id:
            address = Address.query.get(customer.address_id)
            if address:
                customer_data['address'] = address.to_dict()

        # Get customer-specific details and assigned sales
        sales_name = None
        if customer.kind == 0:
            home = Home.query.get(customer.id)
            if home:
                customer_data['details'] = {
                    'gender': home.gender,
                    'age': home.age,
                    'marriage_status': home.marriage_status,
                    'income': home.income
                }
                # Get assigned sales name
                if home.sales_id:
                    sales_employee = Employee.query.get(home.sales_id)
                    if sales_employee:
                        sales_account = OnlineAccount.query.get(sales_employee.online_id)
                        if sales_account:
                            sales_name = sales_account.name
        else:
            business = Business.query.get(customer.id)
            if business:
                customer_data['details'] = {
                    'company_name': business.company_name,
                    'category': business.category,
                    'gross_income': business.gross_income
                }
                # Get assigned sales name
                if business.sales_id:
                    sales_employee = Employee.query.get(business.sales_id)
                    if sales_employee:
                        sales_account = OnlineAccount.query.get(sales_employee.online_id)
                        if sales_account:
                            sales_name = sales_account.name

        customer_data['sales_name'] = sales_name

        # Calculate total spending and order count
        total_spending = db.session.query(func.sum(Orders.total_amount)).filter(
            Orders.customer_id == customer.id,
            Orders.payment_status == True
        ).scalar() or 0
        customer_data['total_spending'] = total_spending

        order_count = Orders.query.filter_by(customer_id=customer.id).count()
        customer_data['order_count'] = order_count

        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            if (search_lower not in customer_data['name'].lower() and
                search_lower not in customer_data['email'].lower()):
                continue

        result.append(customer_data)

    return jsonify({
        'customers': result,
        'total': total,
        'page': page,
        'limit': limit
    }), 200


@bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer_detail(customer_id):
    """Get detailed customer information"""
    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    # Only sales, manager, and region can view customer details
    if role not in ['sales', 'manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    # Check access permissions
    if role == 'sales':
        employee = Employee.query.filter_by(online_id=online_id).first()
        if employee:
            # Check if this customer is assigned to this salesperson
            if customer.kind == 0:
                home = Home.query.get(customer_id)
                if not home or home.sales_id != employee.id:
                    return jsonify({'error': 'Unauthorized to view this customer'}), 403
            else:
                business = Business.query.get(customer_id)
                if not business or business.sales_id != employee.id:
                    return jsonify({'error': 'Unauthorized to view this customer'}), 403

    elif role == 'manager':
        employee = Employee.query.filter_by(online_id=online_id).first()
        if employee:
            salesperson = SalesPerson.query.filter_by(employee_id=employee.id).first()
            if salesperson:
                # Check if customer belongs to a salesperson in this manager's store
                if customer.kind == 0:
                    home = Home.query.get(customer_id)
                    if home and home.sales_id:
                        sales_person = SalesPerson.query.filter_by(employee_id=home.sales_id).first()
                        if not sales_person or sales_person.store_id != salesperson.store_id:
                            return jsonify({'error': 'Unauthorized to view this customer'}), 403
                else:
                    business = Business.query.get(customer_id)
                    if business and business.sales_id:
                        sales_person = SalesPerson.query.filter_by(employee_id=business.sales_id).first()
                        if not sales_person or sales_person.store_id != salesperson.store_id:
                            return jsonify({'error': 'Unauthorized to view this customer'}), 403

    # Get account info
    account = OnlineAccount.query.get(customer.online_id)
    if not account:
        return jsonify({'error': 'Account not found'}), 404

    customer_data = {
        'id': customer.id,
        'online_id': customer.online_id,
        'name': account.name,
        'email': account.email,
        'kind': customer.kind
    }

    # Get address information
    if customer.address_id:
        address = Address.query.get(customer.address_id)
        if address:
            customer_data['address'] = address.to_dict()

    # Get customer-specific details
    sales_id = None
    sales_name = None
    if customer.kind == 0:
        home = Home.query.get(customer_id)
        if home:
            customer_data['details'] = {
                'gender': home.gender,
                'age': home.age,
                'marriage_status': home.marriage_status,
                'income': home.income
            }
            sales_id = home.sales_id
            if home.sales_id:
                sales_employee = Employee.query.get(home.sales_id)
                if sales_employee:
                    sales_account = OnlineAccount.query.get(sales_employee.online_id)
                    if sales_account:
                        sales_name = sales_account.name
    else:
        business = Business.query.get(customer_id)
        if business:
            customer_data['details'] = {
                'company_name': business.company_name,
                'category': business.category,
                'gross_income': business.gross_income
            }
            sales_id = business.sales_id
            if business.sales_id:
                sales_employee = Employee.query.get(business.sales_id)
                if sales_employee:
                    sales_account = OnlineAccount.query.get(sales_employee.online_id)
                    if sales_account:
                        sales_name = sales_account.name

    customer_data['sales_id'] = sales_id
    customer_data['sales_name'] = sales_name

    # Calculate total spending and order count
    total_spending = db.session.query(func.sum(Orders.total_amount)).filter(
        Orders.customer_id == customer_id,
        Orders.payment_status == True
    ).scalar() or 0

    order_count = Orders.query.filter_by(customer_id=customer_id).count()

    customer_data['total_spending'] = total_spending
    customer_data['order_count'] = order_count

    return jsonify(customer_data), 200


@bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """Update customer information"""
    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    # Only sales, manager, and region can update customer info
    if role not in ['sales', 'manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()

    try:
        # Update address information if provided
        if 'address' in data and data['address']:
            address_data = data['address']
            if customer.address_id:
                # Update existing address
                address = Address.query.get(customer.address_id)
                if address:
                    if 'address_1' in address_data:
                        address.address_1 = address_data['address_1']
                    if 'address_2' in address_data:
                        address.address_2 = address_data['address_2']
                    if 'city' in address_data:
                        address.city = address_data['city']
                    if 'state' in address_data:
                        address.state = address_data['state']
                    if 'zipcode' in address_data:
                        address.zipcode = address_data['zipcode']
            else:
                # Create new address
                address = Address(
                    address_1=address_data.get('address_1'),
                    address_2=address_data.get('address_2'),
                    city=address_data.get('city'),
                    state=address_data.get('state'),
                    zipcode=address_data.get('zipcode')
                )
                db.session.add(address)
                db.session.flush()  # Get the address ID
                customer.address_id = address.id

        # Update customer-specific details
        if customer.kind == 0:
            home = Home.query.get(customer_id)
            if home:
                if 'gender' in data:
                    home.gender = data['gender']
                if 'age' in data:
                    home.age = data['age']
                if 'marriage_status' in data:
                    home.marriage_status = data['marriage_status']
                if 'income' in data:
                    home.income = data['income']
                if 'sales_id' in data:
                    # Verify the sales_id is valid
                    if data['sales_id']:
                        sales_employee = Employee.query.get(data['sales_id'])
                        if not sales_employee:
                            return jsonify({'error': 'Invalid sales employee'}), 400
                    home.sales_id = data['sales_id']
        else:
            business = Business.query.get(customer_id)
            if business:
                if 'company_name' in data:
                    business.company_name = data['company_name']
                if 'category' in data:
                    business.category = data['category']
                if 'gross_income' in data:
                    business.gross_income = data['gross_income']
                if 'sales_id' in data:
                    # Verify the sales_id is valid
                    if data['sales_id']:
                        sales_employee = Employee.query.get(data['sales_id'])
                        if not sales_employee:
                            return jsonify({'error': 'Invalid sales employee'}), 400
                    business.sales_id = data['sales_id']

        db.session.commit()
        return jsonify({'message': 'Customer updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/sales-list', methods=['GET'])
@jwt_required()
def get_sales_list():
    """Get list of available sales people for assignment"""
    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    # Only sales, manager, and region can view sales list
    if role not in ['sales', 'manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get all salespeople
    salespeople = SalesPerson.query.all()
    result = []

    for sp in salespeople:
        employee = Employee.query.get(sp.employee_id)
        if employee:
            account = OnlineAccount.query.get(employee.online_id)
            if account:
                result.append({
                    'employee_id': employee.id,
                    'name': account.name,
                    'store_id': sp.store_id
                })

    return jsonify({'salespeople': result}), 200
