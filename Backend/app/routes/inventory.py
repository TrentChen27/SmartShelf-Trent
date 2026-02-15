from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app import db
from app.models.inventory import StoreInventory
from app.models.product import Product
from app.models.store import Store
from app.models.employee import Employee
from app.models.salesperson import SalesPerson

bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')


@bp.route('', methods=['GET'])
@jwt_required()
def get_inventory():
    """Get inventory for stores based on user role"""
    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    # Only manager and region can view inventory
    if role not in ['manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get query parameters
    store_id = request.args.get('store_id', type=int)
    product_id = request.args.get('product_id', type=int)

    # Build query
    query = StoreInventory.query

    # Role-based filtering
    if role == 'manager':
        # Manager can only see inventory from their store
        employee = Employee.query.filter_by(online_id=online_id).first()
        if not employee:
            return jsonify({'inventory': []}), 200

        # Find manager's store
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
            return jsonify({'inventory': []}), 200

        query = query.filter(StoreInventory.store_id == manager_store_id)
    elif role == 'region':
        # Regional manager can see inventory from all stores in their region
        from app.models.region import Region

        employee = Employee.query.filter_by(online_id=online_id).first()
        if employee:
            region = Region.query.filter_by(region_manager=employee.id).first()
            if region:
                # Get all stores in this region
                region_stores = Store.query.filter_by(region_id=region.id).all()
                region_store_ids = [s.id for s in region_stores]

                if region_store_ids:
                    query = query.filter(StoreInventory.store_id.in_(region_store_ids))

    # Additional filters
    if store_id:
        query = query.filter(StoreInventory.store_id == store_id)
    if product_id:
        query = query.filter(StoreInventory.product_id == product_id)

    inventory_items = query.all()

    # Build response with product and store details
    result = []
    for item in inventory_items:
        product = Product.query.get(item.product_id)
        store = Store.query.get(item.store_id)

        inventory_data = item.to_dict()
        if product:
            inventory_data['product'] = product.to_dict()
        if store:
            inventory_data['store_name'] = store.name

        result.append(inventory_data)

    return jsonify({'inventory': result}), 200


@bp.route('', methods=['POST'])
@jwt_required()
def create_or_update_inventory():
    """Create or update inventory for a product at a store"""
    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    # Only manager and region can modify inventory
    if role not in ['manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    # Validate required fields
    if not data.get('store_id') or not data.get('product_id') or 'stock' not in data:
        return jsonify({'error': 'Missing required fields: store_id, product_id, stock'}), 400

    store_id = data['store_id']
    product_id = data['product_id']
    stock = data['stock']

    # Role-based permission check
    if role == 'manager':
        # Manager can only modify inventory for their own store
        employee = Employee.query.filter_by(online_id=online_id).first()
        if not employee:
            return jsonify({'error': 'Unauthorized'}), 403

        # Find manager's store
        salesperson = SalesPerson.query.filter_by(employee_id=employee.id).first()
        manager_store_id = None

        if salesperson:
            manager_store_id = salesperson.store_id
        else:
            managed_store = Store.query.filter_by(manager_id=employee.id).first()
            if managed_store:
                manager_store_id = managed_store.id

        if not manager_store_id or manager_store_id != store_id:
            return jsonify({'error': 'Unauthorized - You can only manage inventory for your own store'}), 403

    try:
        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Check if store exists
        store = Store.query.get(store_id)
        if not store:
            return jsonify({'error': 'Store not found'}), 404

        # Check if inventory record exists
        inventory = StoreInventory.query.filter_by(
            store_id=store_id,
            product_id=product_id
        ).first()

        if inventory:
            # Update existing inventory
            inventory.stock = stock
        else:
            # Create new inventory record
            inventory = StoreInventory(
                store_id=store_id,
                product_id=product_id,
                stock=stock
            )
            db.session.add(inventory)

        db.session.commit()

        return jsonify({
            'message': 'Inventory updated successfully',
            'inventory': inventory.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Inventory update error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:inventory_id>', methods=['DELETE'])
@jwt_required()
def delete_inventory(inventory_id):
    """Delete an inventory record (region only)"""
    claims = get_jwt()
    role = claims.get('role')

    # Only region can delete inventory records
    if role != 'region':
        return jsonify({'error': 'Unauthorized'}), 403

    inventory = StoreInventory.query.get(inventory_id)
    if not inventory:
        return jsonify({'error': 'Inventory record not found'}), 404

    try:
        db.session.delete(inventory)
        db.session.commit()

        return jsonify({'message': 'Inventory deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Delete inventory error: {e}")
        return jsonify({'error': str(e)}), 500
