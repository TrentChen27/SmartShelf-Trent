from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.employee import Employee
from app.models.salesperson import SalesPerson
from app.models.account import OnlineAccount
from app.models.store import Store
from app.models.region import Region

bp = Blueprint('employees', __name__, url_prefix='/api/employees')


@bp.route('', methods=['GET'])
@jwt_required()
def get_employees():
    """Get employees list (for manager, region roles)"""
    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    # Only manager and region can view employees
    if role not in ['manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get query parameters
    search = request.args.get('search', '')
    store_id = request.args.get('store_id', type=int)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)

    # Limit maximum page size
    limit = min(limit, 100)

    # Build query
    query = Employee.query

    # Role-based filtering
    if role == 'manager':
        # Manager can only see employees from their store
        employee = Employee.query.filter_by(online_id=online_id).first()
        if not employee:
            return jsonify({'employees': [], 'total': 0, 'page': page, 'limit': limit}), 200

        # Try to find store by salesperson record first
        salesperson = SalesPerson.query.filter_by(employee_id=employee.id).first()
        manager_store_id = None

        if salesperson:
            manager_store_id = salesperson.store_id
        else:
            # If not a salesperson, check if they are a store manager
            managed_store = Store.query.filter_by(manager_id=employee.id).first()
            if managed_store:
                manager_store_id = managed_store.id

        if not manager_store_id:
            return jsonify({'employees': [], 'total': 0, 'page': page, 'limit': limit}), 200

        # Get all employees from this store (including manager and salespeople)
        store_salespeople = SalesPerson.query.filter_by(store_id=manager_store_id).all()
        employee_ids = [sp.employee_id for sp in store_salespeople]

        # Also include the manager themselves
        if employee.id not in employee_ids:
            employee_ids.append(employee.id)

        if employee_ids:
            query = query.filter(Employee.id.in_(employee_ids))
        else:
            return jsonify({'employees': [], 'total': 0, 'page': page, 'limit': limit}), 200

    elif role == 'region':
        # Region manager can only see employees from their region's stores
        employee = Employee.query.filter_by(online_id=online_id).first()
        if not employee:
            return jsonify({'employees': [], 'total': 0, 'page': page, 'limit': limit}), 200

        # Find the region this manager manages
        region = Region.query.filter_by(region_manager=employee.id).first()
        if not region:
            return jsonify({'employees': [], 'total': 0, 'page': page, 'limit': limit}), 200

        # Get all stores in this region
        region_stores = Store.query.filter_by(region_id=region.id).all()
        region_store_ids = [s.id for s in region_stores]

        if not region_store_ids:
            return jsonify({'employees': [], 'total': 0, 'page': page, 'limit': limit}), 200

        # Get all employees from these stores (both salespeople and managers)
        employee_ids = set()

        # Add all salespeople from region stores
        region_salespeople = SalesPerson.query.filter(SalesPerson.store_id.in_(region_store_ids)).all()
        for sp in region_salespeople:
            employee_ids.add(sp.employee_id)

        # Add all store managers from region stores
        for store in region_stores:
            if store.manager_id:
                employee_ids.add(store.manager_id)

        # Also include the regional manager themselves
        employee_ids.add(employee.id)

        if employee_ids:
            query = query.filter(Employee.id.in_(list(employee_ids)))
        else:
            return jsonify({'employees': [], 'total': 0, 'page': page, 'limit': limit}), 200

    # Additional filters
    if store_id:
        # Filter by store
        store_salespeople = SalesPerson.query.filter_by(store_id=store_id).all()
        employee_ids = [sp.employee_id for sp in store_salespeople]
        if employee_ids:
            query = query.filter(Employee.id.in_(employee_ids))
        else:
            return jsonify({'employees': [], 'total': 0, 'page': page, 'limit': limit}), 200

    # Apply search filter at SQL level by joining with OnlineAccount
    if search:
        search_pattern = f'%{search}%'
        query = query.join(OnlineAccount, Employee.online_id == OnlineAccount.online_id).filter(
            db.or_(
                OnlineAccount.name.ilike(search_pattern),
                OnlineAccount.email.ilike(search_pattern)
            )
        )

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    employees_list = query.offset(offset).limit(limit).all()

    # Build response with employee details
    result = []
    for emp in employees_list:
        # Get account info
        account = OnlineAccount.query.get(emp.online_id)
        if not account:
            continue

        employee_data = {
            'id': emp.id,
            'online_id': emp.online_id,
            'name': account.name,
            'email': account.email,
            'job_title': emp.job_title,
            'salary': emp.salary
        }

        # Check if this employee is a regional manager
        region = Region.query.filter_by(region_manager=emp.id).first()
        if region:
            employee_data['is_region_manager'] = True
            employee_data['is_salesperson'] = False
            employee_data['is_manager'] = False
            employee_data['store_name'] = None
        else:
            employee_data['is_region_manager'] = False

        # Get salesperson info if applicable
        salesperson = SalesPerson.query.filter_by(employee_id=emp.id).first()
        if salesperson:
            employee_data['is_salesperson'] = True
            employee_data['store_id'] = salesperson.store_id

            # Get store info
            store = Store.query.get(salesperson.store_id)
            if store:
                employee_data['store_name'] = store.name

                # Check if this employee is the store manager
                employee_data['is_manager'] = (store.manager_id == emp.id)
        else:
            # Check if they are a store manager (without salesperson record)
            managed_store = Store.query.filter_by(manager_id=emp.id).first()
            if managed_store:
                employee_data['is_manager'] = True
                employee_data['is_salesperson'] = False
                employee_data['store_name'] = managed_store.name
                employee_data['store_id'] = managed_store.id
            else:
                employee_data['is_salesperson'] = False
                employee_data['is_manager'] = False

        result.append(employee_data)

    return jsonify({
        'employees': result,
        'total': total,
        'page': page,
        'limit': limit
    }), 200


@bp.route('', methods=['POST'])
@jwt_required()
def create_employee():
    """Create a new employee (for manager, region roles)"""
    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    # Only manager and region can create employees
    if role not in ['manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    # Validate required fields
    required_fields = ['name', 'email', 'passwd', 'job_title', 'salary']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        # Check if email already exists
        existing_account = OnlineAccount.query.filter_by(email=data['email']).first()
        if existing_account:
            return jsonify({'error': 'Email already exists'}), 400

        # Create online account
        account = OnlineAccount(
            name=data['name'],
            email=data['email']
        )
        account.set_password(data['passwd'])
        db.session.add(account)
        db.session.flush()

        # Create employee
        employee = Employee(
            online_id=account.online_id,
            job_title=data['job_title'],
            salary=data['salary']
        )
        db.session.add(employee)
        db.session.flush()

        # If role is manager, can only assign to their own store
        if role == 'manager':
            manager_employee = Employee.query.filter_by(online_id=online_id).first()
            if manager_employee:
                manager_salesperson = SalesPerson.query.filter_by(employee_id=manager_employee.id).first()
                if manager_salesperson and data.get('is_salesperson'):
                    # Assign to manager's store
                    salesperson = SalesPerson(
                        employee_id=employee.id,
                        store_id=manager_salesperson.store_id
                    )
                    db.session.add(salesperson)

        # If role is region, can assign to any store and set as manager
        elif role == 'region':
            if data.get('is_salesperson') and data.get('store_id'):
                # Verify store exists
                store = Store.query.get(data['store_id'])
                if not store:
                    db.session.rollback()
                    return jsonify({'error': 'Invalid store'}), 400

                # Check if store is in region manager's region
                manager_employee = Employee.query.filter_by(online_id=online_id).first()
                if manager_employee:
                    region = Region.query.filter_by(region_manager=manager_employee.id).first()
                    if region and store.region_id != region.id:
                        db.session.rollback()
                        return jsonify({'error': 'You can only assign employees to stores in your region'}), 403

                salesperson = SalesPerson(
                    employee_id=employee.id,
                    store_id=data['store_id']
                )
                db.session.add(salesperson)

                # Set as store manager if requested
                if data.get('is_manager'):
                    # Check if store already has a manager
                    if store.manager_id and store.manager_id != employee.id:
                        existing_manager = Employee.query.get(store.manager_id)
                        if existing_manager:
                            manager_account = OnlineAccount.query.get(existing_manager.online_id)
                            manager_name = manager_account.name if manager_account else 'Unknown'
                            db.session.rollback()
                            return jsonify({
                                'error': f'Store "{store.name}" already has a manager: {manager_name}. Each store can only have one manager.'
                            }), 400

                    store.manager_id = employee.id

        db.session.commit()

        return jsonify({
            'message': 'Employee created successfully',
            'employee_id': employee.id
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Create employee error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    """Update employee information (for manager, region roles)"""
    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    # Only manager and region can update employees
    if role not in ['manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    data = request.get_json()

    try:
        # Update basic employee info
        if 'job_title' in data:
            employee.job_title = data['job_title']
        if 'salary' in data:
            employee.salary = data['salary']

        # Region manager can update store assignment and manager status
        if role == 'region':
            salesperson = SalesPerson.query.filter_by(employee_id=employee_id).first()

            # Handle salesperson status change
            if 'is_salesperson' in data:
                if data['is_salesperson'] and not salesperson:
                    # Add as salesperson
                    if 'store_id' not in data:
                        return jsonify({'error': 'store_id required to make employee a salesperson'}), 400

                    salesperson = SalesPerson(
                        employee_id=employee_id,
                        store_id=data['store_id']
                    )
                    db.session.add(salesperson)
                elif not data['is_salesperson'] and salesperson:
                    # Remove from salesperson (also removes manager status)
                    store = Store.query.get(salesperson.store_id)
                    if store and store.manager_id == employee_id:
                        store.manager_id = None
                    db.session.delete(salesperson)
                    salesperson = None

            # Update store assignment if salesperson
            if salesperson and 'store_id' in data:
                old_store_id = salesperson.store_id
                salesperson.store_id = data['store_id']

                # If was manager of old store, remove manager status
                old_store = Store.query.get(old_store_id)
                if old_store and old_store.manager_id == employee_id:
                    old_store.manager_id = None

            # Update manager status
            if 'is_manager' in data and salesperson:
                store = Store.query.get(salesperson.store_id)
                if store:
                    if data['is_manager']:
                        # Check if store already has a different manager
                        if store.manager_id and store.manager_id != employee_id:
                            existing_manager = Employee.query.get(store.manager_id)
                            if existing_manager:
                                manager_account = OnlineAccount.query.get(existing_manager.online_id)
                                manager_name = manager_account.name if manager_account else 'Unknown'
                                db.session.rollback()
                                return jsonify({
                                    'error': f'Store "{store.name}" already has a manager: {manager_name}. Each store can only have one manager.'
                                }), 400
                        store.manager_id = employee_id
                    elif store.manager_id == employee_id:
                        store.manager_id = None

        db.session.commit()
        return jsonify({'message': 'Employee updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Update employee error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    """Delete an employee (region only)"""
    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    # Only region can delete employees
    if role != 'region':
        return jsonify({'error': 'Unauthorized - Only region managers can delete employees'}), 403

    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    try:
        # Check if employee is a store manager
        store = Store.query.filter_by(manager_id=employee_id).first()
        if store:
            return jsonify({'error': 'Cannot delete employee who is a store manager. Please reassign manager first.'}), 400

        # Delete salesperson record if exists
        salesperson = SalesPerson.query.filter_by(employee_id=employee_id).first()
        if salesperson:
            db.session.delete(salesperson)

        # Delete employee
        db.session.delete(employee)

        # Delete online account
        account = OnlineAccount.query.get(employee.online_id)
        if account:
            db.session.delete(account)

        db.session.commit()
        return jsonify({'message': 'Employee deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Delete employee error: {e}")
        return jsonify({'error': str(e)}), 500
