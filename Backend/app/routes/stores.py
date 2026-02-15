from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app import db
from app.models.store import Store
from app.models.inventory import StoreInventory
from app.models.product import Product
from app.models.employee import Employee
from app.models.salesperson import SalesPerson

bp = Blueprint('stores', __name__, url_prefix='/api/stores')


def get_manager_store_id(online_id):
    """Helper function to get the store ID for a manager"""
    employee = Employee.query.filter_by(online_id=online_id).first()
    if not employee:
        return None

    # Try to find store by salesperson record first
    salesperson = SalesPerson.query.filter_by(employee_id=employee.id).first()
    if salesperson:
        return salesperson.store_id

    # If not a salesperson, check if they are a store manager
    managed_store = Store.query.filter_by(manager_id=employee.id).first()
    if managed_store:
        return managed_store.id

    return None


@bp.route('', methods=['GET'])
@jwt_required(optional=True)
def get_stores():
    """Get all stores (role-based filtering)."""
    from app.models.region import Region

    region_id = request.args.get('region_id')

    # Check if user is authenticated
    current_user_id = get_jwt_identity()
    claims = get_jwt() if current_user_id else {}
    role = claims.get('role') if claims else None

    query = Store.query

    # Role-based filtering
    if role == 'region' and current_user_id:
        # Regional manager sees only their region's stores
        online_id = int(current_user_id)
        employee = Employee.query.filter_by(online_id=online_id).first()
        if employee:
            region = Region.query.filter_by(region_manager=employee.id).first()
            if region:
                query = query.filter_by(region_id=region.id)
    elif region_id:
        # Filter by specific region if provided
        query = query.filter_by(region_id=region_id)

    stores = query.all()

    # Include manager and region info
    result = []
    for store in stores:
        store_dict = store.to_dict(include_address=True)

        # Add manager name
        if store.manager_id:
            manager_emp = Employee.query.get(store.manager_id)
            if manager_emp:
                from app.models.account import OnlineAccount
                manager_account = OnlineAccount.query.get(manager_emp.online_id)
                if manager_account:
                    store_dict['manager_name'] = manager_account.name

        # Add region name
        if store.region_id:
            region = Region.query.get(store.region_id)
            if region:
                store_dict['region_name'] = region.region_name

        result.append(store_dict)

    return jsonify(result), 200


@bp.route('/<int:store_id>', methods=['GET'])
def get_store(store_id):
    """Get a specific store by ID."""
    store = Store.query.get(store_id)

    if not store:
        return jsonify({'error': 'Store not found'}), 404

    return jsonify(store.to_dict(include_address=True)), 200


@bp.route('/<int:store_id>/inventory', methods=['GET'])
def get_store_inventory(store_id):
    """Get all inventory for a specific store."""
    store = Store.query.get(store_id)

    if not store:
        return jsonify({'error': 'Store not found'}), 404

    inventory_items = StoreInventory.query.filter_by(store_id=store_id).all()

    result = []
    for item in inventory_items:
        product = Product.query.get(item.product_id)
        if product:
            inventory_data = item.to_dict()
            inventory_data['product'] = product.to_dict()
            result.append(inventory_data)

    return jsonify(result), 200


@bp.route('/<int:store_id>/inventory/<int:product_id>', methods=['GET'])
def get_product_inventory(store_id, product_id):
    """Get inventory for a specific product at a specific store."""
    inventory = StoreInventory.query.filter_by(
        store_id=store_id,
        product_id=product_id
    ).first()

    if not inventory:
        return jsonify({'stock': 0}), 200

    return jsonify(inventory.to_dict()), 200


@bp.route('/<int:store_id>/inventory', methods=['POST'])
@jwt_required()
def add_or_update_inventory(store_id):
    """Add or update inventory for a store (manager only)"""
    claims = get_jwt()
    role = claims.get('role')

    if role not in ['manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Store managers can only modify their own store's inventory
    if role == 'manager':
        online_id = int(get_jwt_identity())
        manager_store_id = get_manager_store_id(online_id)

        if not manager_store_id or manager_store_id != store_id:
            return jsonify({'error': 'Unauthorized - You can only modify your own store'}), 403

    data = request.get_json()

    if not data.get('product_id') or 'stock' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Check if inventory exists
        inventory = StoreInventory.query.filter_by(
            store_id=store_id,
            product_id=data['product_id']
        ).first()

        if inventory:
            # Update existing inventory
            inventory.stock = data['stock']
        else:
            # Create new inventory entry
            inventory = StoreInventory(
                store_id=store_id,
                product_id=data['product_id'],
                stock=data['stock']
            )
            db.session.add(inventory)

        db.session.commit()

        return jsonify(inventory.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        print(f"Inventory update error: {e}")
        return jsonify({'error': 'Failed to update inventory'}), 500


@bp.route('/<int:store_id>/inventory/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_inventory(store_id, product_id):
    """Update inventory stock (manager only)"""
    claims = get_jwt()
    role = claims.get('role')

    if role not in ['manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Store managers can only modify their own store's inventory
    if role == 'manager':
        online_id = int(get_jwt_identity())
        manager_store_id = get_manager_store_id(online_id)

        if not manager_store_id or manager_store_id != store_id:
            return jsonify({'error': 'Unauthorized - You can only modify your own store'}), 403

    inventory = StoreInventory.query.filter_by(
        store_id=store_id,
        product_id=product_id
    ).first()

    if not inventory:
        return jsonify({'error': 'Inventory not found'}), 404

    data = request.get_json()

    if 'stock' not in data:
        return jsonify({'error': 'Missing stock field'}), 400

    try:
        inventory.stock = data['stock']
        db.session.commit()

        return jsonify(inventory.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        print(f"Inventory update error: {e}")
        return jsonify({'error': 'Failed to update inventory'}), 500


@bp.route('/<int:store_id>/inventory/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_inventory(store_id, product_id):
    """Remove product from store inventory (manager only)"""
    claims = get_jwt()
    role = claims.get('role')

    if role not in ['manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Store managers can only modify their own store's inventory
    if role == 'manager':
        online_id = int(get_jwt_identity())
        manager_store_id = get_manager_store_id(online_id)

        if not manager_store_id or manager_store_id != store_id:
            return jsonify({'error': 'Unauthorized - You can only modify your own store'}), 403

    inventory = StoreInventory.query.filter_by(
        store_id=store_id,
        product_id=product_id
    ).first()

    if not inventory:
        return jsonify({'error': 'Inventory not found'}), 404

    try:
        db.session.delete(inventory)
        db.session.commit()

        return jsonify({'message': 'Inventory deleted'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Inventory delete error: {e}")
        return jsonify({'error': 'Failed to delete inventory'}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_store():
    """Create a new store (region manager only)"""
    from app.models.region import Region
    from app.models.address import Address

    claims = get_jwt()
    role = claims.get('role')

    # Only regional managers can create stores
    if role != 'region':
        return jsonify({'error': 'Unauthorized - Only regional managers can create stores'}), 403

    online_id = int(get_jwt_identity())
    data = request.get_json()

    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'Store name is required'}), 400

    try:
        # Get the regional manager's region
        employee = Employee.query.filter_by(online_id=online_id).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        region = Region.query.filter_by(region_manager=employee.id).first()
        if not region:
            return jsonify({'error': 'Region not found'}), 404

        # Create address if provided
        address_id = None
        if data.get('address'):
            address_data = data['address']
            address = Address(
                address_1=address_data.get('address_1'),
                address_2=address_data.get('address_2'),
                city=address_data.get('city'),
                state=address_data.get('state'),
                zipcode=address_data.get('zipcode')
            )
            db.session.add(address)
            db.session.flush()
            address_id = address.id

        # Create store
        store = Store(
            name=data['name'],
            region_id=region.id,
            address_id=address_id,
            manager_id=data.get('manager_id')  # Optional
        )
        db.session.add(store)
        db.session.commit()

        return jsonify(store.to_dict(include_address=True)), 201

    except Exception as e:
        db.session.rollback()
        print(f"Create store error: {e}")
        return jsonify({'error': 'Failed to create store'}), 500


@bp.route('/<int:store_id>', methods=['PUT'])
@jwt_required()
def update_store(store_id):
    """Update a store (region manager only)"""
    from app.models.region import Region
    from app.models.address import Address

    claims = get_jwt()
    role = claims.get('role')

    # Only regional managers can update stores
    if role != 'region':
        return jsonify({'error': 'Unauthorized - Only regional managers can update stores'}), 403

    online_id = int(get_jwt_identity())
    data = request.get_json()

    store = Store.query.get(store_id)
    if not store:
        return jsonify({'error': 'Store not found'}), 404

    try:
        # Verify the store belongs to this regional manager's region
        employee = Employee.query.filter_by(online_id=online_id).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        region = Region.query.filter_by(region_manager=employee.id).first()
        if not region or store.region_id != region.id:
            return jsonify({'error': 'Unauthorized - Store not in your region'}), 403

        # Update store name
        if 'name' in data:
            store.name = data['name']

        # Update manager
        if 'manager_id' in data:
            store.manager_id = data['manager_id']

        # Update address
        if 'address' in data:
            address_data = data['address']
            if store.address_id:
                # Update existing address
                address = Address.query.get(store.address_id)
                if address:
                    address.address_1 = address_data.get('address_1', address.address_1)
                    address.address_2 = address_data.get('address_2', address.address_2)
                    address.city = address_data.get('city', address.city)
                    address.state = address_data.get('state', address.state)
                    address.zipcode = address_data.get('zipcode', address.zipcode)
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
                db.session.flush()
                store.address_id = address.id

        db.session.commit()

        return jsonify(store.to_dict(include_address=True)), 200

    except Exception as e:
        db.session.rollback()
        print(f"Update store error: {e}")
        return jsonify({'error': 'Failed to update store'}), 500


@bp.route('/<int:store_id>', methods=['DELETE'])
@jwt_required()
def delete_store(store_id):
    """Delete a store (region manager only)"""
    from app.models.region import Region

    claims = get_jwt()
    role = claims.get('role')

    # Only regional managers can delete stores
    if role != 'region':
        return jsonify({'error': 'Unauthorized - Only regional managers can delete stores'}), 403

    online_id = int(get_jwt_identity())

    store = Store.query.get(store_id)
    if not store:
        return jsonify({'error': 'Store not found'}), 404

    try:
        # Verify the store belongs to this regional manager's region
        employee = Employee.query.filter_by(online_id=online_id).first()
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        region = Region.query.filter_by(region_manager=employee.id).first()
        if not region or store.region_id != region.id:
            return jsonify({'error': 'Unauthorized - Store not in your region'}), 403

        # Check if store has inventory
        inventory_count = StoreInventory.query.filter_by(store_id=store_id).count()
        if inventory_count > 0:
            return jsonify({'error': 'Cannot delete store with existing inventory. Please remove all inventory first.'}), 400

        # Check if store has employees
        employees_count = SalesPerson.query.filter_by(store_id=store_id).count()
        if employees_count > 0:
            return jsonify({'error': 'Cannot delete store with assigned employees. Please reassign employees first.'}), 400

        db.session.delete(store)
        db.session.commit()

        return jsonify({'message': 'Store deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Delete store error: {e}")
        return jsonify({'error': 'Failed to delete store'}), 500
