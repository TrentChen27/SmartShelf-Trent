from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models.product import Product
from app.models.inventory import StoreInventory
from app.models.store import Store

bp = Blueprint('products', __name__, url_prefix='/api/products')


@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all unique product categories"""
    categories = db.session.query(Product.kind).distinct().filter(Product.kind.isnot(None)).all()
    category_list = [cat[0] for cat in categories if cat[0]]
    return jsonify(sorted(category_list)), 200


@bp.route('', methods=['GET'])
def get_products():
    """Get all products with optional store filtering"""
    # Query parameters
    store_id = request.args.get('store_id')  # Filter by store (only in-stock)

    query = Product.query

    # If store_id is provided, only return products in stock at that store
    if store_id:
        inventory_items = StoreInventory.query.filter(
            StoreInventory.store_id == store_id,
            StoreInventory.stock > 0
        ).all()
        
        in_stock_product_ids = [item.product_id for item in inventory_items]
        if in_stock_product_ids:
            query = query.filter(Product.id.in_(in_stock_product_ids))
        else:
            # No products in stock at this store
            return jsonify([]), 200

    products = query.all()

    # Get all inventory in one query
    all_inventory = StoreInventory.query.all()
    
    # Get all stores in one query
    all_stores = Store.query.all()
    stores_dict = {s.id: s.name for s in all_stores}
    
    # Build inventory map: product_id -> list of inventories
    inventory_map = {}
    for inv in all_inventory:
        if inv.product_id not in inventory_map:
            inventory_map[inv.product_id] = []
        inventory_map[inv.product_id].append({
            'store_id': inv.store_id,
            'store_name': stores_dict.get(inv.store_id, f'Store {inv.store_id}'),
            'stock': inv.stock
        })

    # Build result with inventory information
    result = []
    for p in products:
        product_dict = p.to_dict()
        product_dict['stores_inventory'] = inventory_map.get(p.id, [])
        result.append(product_dict)

    return jsonify(result), 200


@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID with all stores inventory"""
    product = Product.query.get(product_id)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Get product basic info
    product_data = product.to_dict()

    # Get inventory from all stores
    inventory_items = StoreInventory.query.filter_by(product_id=product_id).all()
    
    # Build stores inventory map
    stores_inventory = {}
    for item in inventory_items:
        stores_inventory[item.store_id] = {
            'stock': item.stock,
            'store_id': item.store_id
        }
    
    product_data['stores_inventory'] = stores_inventory

    return jsonify(product_data), 200


@bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """Create a new product (admin/manager only)"""
    claims = get_jwt()
    if claims.get('role') not in ['manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    if not data.get('product_name') or not data.get('price'):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        product = Product(
            product_name=data['product_name'],
            price=data['price'],
            kind=data.get('kind'),
            description=data.get('description'),
            image_url=data.get('image_url')
        )

        db.session.add(product)
        db.session.commit()

        return jsonify(product.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(f"Create product error: {e}")
        return jsonify({'error': 'Failed to create product'}), 500


@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update a product (admin/manager only)"""
    claims = get_jwt()
    if claims.get('role') not in ['manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()

    try:
        if 'product_name' in data:
            product.product_name = data['product_name']
        if 'price' in data:
            product.price = data['price']
        if 'kind' in data:
            product.kind = data['kind']
        if 'description' in data:
            product.description = data['description']
        if 'image_url' in data:
            product.image_url = data['image_url']

        db.session.commit()

        return jsonify(product.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        print(f"Update product error: {e}")
        return jsonify({'error': 'Failed to update product'}), 500


@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete a product (admin only)"""
    claims = get_jwt()
    if claims.get('role') != 'region':
        return jsonify({'error': 'Unauthorized'}), 403

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    try:
        db.session.delete(product)
        db.session.commit()

        return jsonify({'message': 'Product deleted'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Delete product error: {e}")
        return jsonify({'error': 'Failed to delete product'}), 500
