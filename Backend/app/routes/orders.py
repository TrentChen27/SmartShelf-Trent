from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.order import Orders, OrderItem
from app.models.customer import Customer, Home, Business
from app.models.inventory import StoreInventory
from app.models.product import Product
from app.models.store import Store
from app.models.salesperson import SalesPerson
import random

bp = Blueprint('orders', __name__, url_prefix='/api/orders')


@bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order"""
    online_id = int(get_jwt_identity())
    data = request.get_json()

    # Get customer
    customer = Customer.query.filter_by(online_id=online_id).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    # Validate required fields
    if not data.get('store_id') or not data.get('items'):
        return jsonify({'error': 'Missing required fields'}), 400

    # Determine sales_id
    sales_id = None

    # Check if customer has their own sales person
    if customer.kind == 0:  # Home customer
        home = Home.query.get(customer.id)
        if home and home.sales_id:
            sales_id = home.sales_id
    elif customer.kind == 1:  # Business customer
        business = Business.query.get(customer.id)
        if business and business.sales_id:
            sales_id = business.sales_id

    # If customer doesn't have their own sales, assign one randomly from the store
    if not sales_id:
        store_id = data['store_id']
        # Get all salespeople from this store
        salespeople = SalesPerson.query.filter_by(store_id=store_id).all()
        if salespeople:
            # Randomly assign one
            selected_sales = random.choice(salespeople)
            sales_id = selected_sales.employee_id
        else:
            # No salespeople available for this store
            return jsonify({'error': f'No salespeople available for store {store_id}'}), 400

    try:
        # Calculate total
        total_amount = 0
        order_items = []

        for item in data['items']:
            # Check inventory
            inventory = StoreInventory.query.filter_by(
                store_id=data['store_id'],
                product_id=item['product_id']
            ).first()

            if not inventory or inventory.stock < item['quantity']:
                return jsonify({'error': f'Insufficient stock for product {item["product_id"]}'}), 400

            sub_price = item['price'] * item['quantity']
            total_amount += sub_price

            order_items.append({
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'sub_price': sub_price
            })

            # Reduce inventory
            inventory.stock -= item['quantity']

        # Create order
        order = Orders(
            customer_id=customer.id,
            store_id=data['store_id'],
            sales_id=sales_id,
            total_amount=total_amount,
            payment_status=False,
            pickup_status=0
        )
        db.session.add(order)
        db.session.flush()

        # Create order items
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                **item_data
            )
            db.session.add(order_item)

        db.session.commit()

        return jsonify(order.to_dict(include_items=True)), 201

    except Exception as e:
        db.session.rollback()
        print(f"Create order error: {e}")
        return jsonify({'error': 'Failed to create order'}), 500


@bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Get orders (filtered by user role)"""
    from sqlalchemy.orm import joinedload
    from sqlalchemy import or_
    from app.models.account import OnlineAccount

    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    # Get filter parameters
    customer_id = request.args.get('customer_id')
    sales_id = request.args.get('sales_id')
    store_id = request.args.get('store_id')
    status = request.args.get('status')
    search = request.args.get('search', '').strip()

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)  # Default limit to 20 orders per page

    # Use eager loading to prevent N+1 queries
    query = Orders.query.options(
        joinedload(Orders.items).joinedload(OrderItem.product),
        joinedload(Orders.store)
    )

    if role == 'customer':
        customer = Customer.query.filter_by(online_id=online_id).first()
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        query = query.filter_by(customer_id=customer.id)
    elif role == 'sales':
        # Sales can view their own orders
        from app.models.employee import Employee
        from app.models.salesperson import SalesPerson
        employee = Employee.query.filter_by(online_id=online_id).first()
        if employee:
            salesperson = SalesPerson.query.filter_by(employee_id=employee.id).first()
            if salesperson:
                query = query.filter_by(sales_id=salesperson.employee_id)
    elif role == 'manager':
        # Manager can view orders from their store
        from app.models.employee import Employee
        from app.models.salesperson import SalesPerson
        employee = Employee.query.filter_by(online_id=online_id).first()
        if employee:
            salesperson = SalesPerson.query.filter_by(employee_id=employee.id).first()
            if salesperson:
                query = query.filter_by(store_id=salesperson.store_id)
    # Region managers can view all orders (no filter needed)

    # Apply additional filters
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if sales_id:
        query = query.filter_by(sales_id=sales_id)
    if store_id:
        query = query.filter_by(store_id=store_id)
    if status is not None:
        query = query.filter_by(pickup_status=int(status))

    # Apply search filter (search by customer name, email, or product name)
    if search:
        # Join with Customer and OnlineAccount to search by customer name/email
        query = query.join(Customer, Orders.customer_id == Customer.id)
        query = query.join(OnlineAccount, Customer.online_id == OnlineAccount.id)

        # Also join with OrderItem and Product to search by product name
        query = query.join(OrderItem, Orders.id == OrderItem.order_id)
        query = query.join(Product, OrderItem.product_id == Product.id)

        # Search across customer name, email, and product name
        search_pattern = f'%{search}%'
        query = query.filter(
            or_(
                OnlineAccount.name.ilike(search_pattern),
                OnlineAccount.email.ilike(search_pattern),
                Product.product_name.ilike(search_pattern)
            )
        ).distinct()

    # Get total count before pagination
    total_count = query.count()

    # Calculate offset for pagination
    offset = (page - 1) * limit

    # Order by date and apply pagination
    orders = query.order_by(Orders.order_date.desc()).offset(offset).limit(limit).all()

    # Include customer name and sales name for non-customer roles
    include_customer = role in ['sales', 'manager', 'region']
    include_sales = role in ['manager', 'region']  # Only managers and region can see sales info

    return jsonify({
        'orders': [o.to_dict(include_items=True, include_store=True, include_customer_name=include_customer, include_sales_name=include_sales) for o in orders],
        'total': total_count,
        'page': page,
        'limit': limit
    }), 200


@bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get a specific order"""
    order = Orders.query.get(order_id)

    if not order:
        return jsonify({'error': 'Order not found'}), 404

    # TODO: Add authorization check

    return jsonify(order.to_dict(include_items=True)), 200


@bp.route('/<int:order_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order"""
    online_id = int(get_jwt_identity())

    order = Orders.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    # Check authorization
    customer = Customer.query.filter_by(online_id=online_id).first()
    if not customer or order.customer_id != customer.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Can only cancel if order is in ordered (0) or pending (1) status
    if order.pickup_status not in [0, 1]:
        return jsonify({'error': 'Cannot cancel this order'}), 400

    try:
        # Restore inventory
        for item in order.items:
            inventory = StoreInventory.query.filter_by(
                store_id=order.store_id,
                product_id=item.product_id
            ).first()
            if inventory:
                inventory.stock += item.quantity

        # Update order status
        order.pickup_status = 3  # Cancelled

        db.session.commit()

        return jsonify(order.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        print(f"Cancel order error: {e}")
        return jsonify({'error': 'Failed to cancel order'}), 500


@bp.route('/<int:order_id>/request-modification', methods=['POST'])
@jwt_required()
def request_modification(order_id):
    """Request order modification (requires sales approval)"""
    online_id = int(get_jwt_identity())
    data = request.get_json()

    order = Orders.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    # Check authorization
    customer = Customer.query.filter_by(online_id=online_id).first()
    if not customer or order.customer_id != customer.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if order.pickup_status != 0:
        return jsonify({'error': 'Cannot modify this order'}), 400

    # For now, we'll store the modification request as a simple note
    # In a full implementation, you'd have a ModificationRequest table

    try:
        # Store modification request details
        # TODO: Create a proper ModificationRequest model
        modification_data = {
            'order_id': order_id,
            'requested_items': data.get('items', []),
            'reason': data.get('reason', ''),
            'status': 'pending'  # pending, approved, rejected
        }

        # For now, just return success
        # In production, you'd save this to a ModificationRequest table
        return jsonify({
            'message': 'Modification request submitted successfully',
            'request': modification_data
        }), 200

    except Exception as e:
        print(f"Request modification error: {e}")
        return jsonify({'error': 'Failed to submit modification request'}), 500


@bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """Update order pickup status (for sales/manager/region)"""
    from app.models.order import get_eastern_time
    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')
    data = request.get_json()

    # Only sales, manager, and region can update order status
    if role not in ['sales', 'manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    order = Orders.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    new_status = data.get('pickup_status')
    if new_status is None:
        return jsonify({'error': 'pickup_status is required'}), 400

    # Valid statuses: 0=ordered, 1=pending, 2=complete, 3=cancelled
    if new_status not in [0, 1, 2, 3]:
        return jsonify({'error': 'Invalid status value'}), 400

    # Prevent marking as complete (picked up) if not paid
    if new_status == 2 and not order.payment_status:
        return jsonify({'error': 'Cannot mark unpaid order as complete'}), 400

    try:
        # If cancelling, restore inventory
        if new_status == 3 and order.pickup_status != 3:
            for item in order.items:
                inventory = StoreInventory.query.filter_by(
                    store_id=order.store_id,
                    product_id=item.product_id
                ).first()
                if inventory:
                    inventory.stock += item.quantity

        # Update pickup_date when marking as complete (picked up)
        if new_status == 2:
            order.pickup_date = get_eastern_time()

        order.pickup_status = new_status
        db.session.commit()

        return jsonify(order.to_dict(include_items=True, include_store=True)), 200

    except Exception as e:
        db.session.rollback()
        print(f"Update order status error: {e}")
        return jsonify({'error': 'Failed to update order status'}), 500


@bp.route('/<int:order_id>/payment', methods=['PUT'])
@jwt_required()
def update_payment_status(order_id):
    """Update order payment status (for sales/manager/region)"""
    online_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')
    data = request.get_json()

    # Only sales, manager, and region can update payment status
    if role not in ['sales', 'manager', 'region']:
        return jsonify({'error': 'Unauthorized'}), 403

    order = Orders.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    payment_status = data.get('payment_status')
    if payment_status is None:
        return jsonify({'error': 'payment_status is required'}), 400

    try:
        order.payment_status = bool(payment_status)
        db.session.commit()

        return jsonify(order.to_dict(include_items=True, include_store=True)), 200

    except Exception as e:
        db.session.rollback()
        print(f"Update payment status error: {e}")
        return jsonify({'error': 'Failed to update payment status'}), 500


@bp.route('/<int:order_id>/process-payment', methods=['POST'])
@jwt_required()
def process_payment(order_id):
    """Process credit card payment for an order"""
    online_id = int(get_jwt_identity())
    data = request.get_json()

    order = Orders.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    # Check authorization - only the order owner can pay
    customer = Customer.query.filter_by(online_id=online_id).first()
    if not customer or order.customer_id != customer.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Check if already paid
    if order.payment_status:
        return jsonify({'error': 'Order is already paid'}), 400

    # Validate payment data
    card_number = data.get('cardNumber', '')
    cardholder_name = data.get('cardholderName', '')
    expiry_date = data.get('expiryDate', '')
    cvv = data.get('cvv', '')

    if not all([card_number, cardholder_name, expiry_date, cvv]):
        return jsonify({'error': 'Missing payment information'}), 400

    # Basic validation (in a real system, you'd use a payment gateway)
    import re

    # Validate card number (13-19 digits)
    if not re.match(r'^\d{13,19}$', card_number):
        return jsonify({'error': 'Invalid card number format'}), 400

    # Validate expiry date (MM/YY)
    if not re.match(r'^\d{2}/\d{2}$', expiry_date):
        return jsonify({'error': 'Invalid expiry date format'}), 400

    # Validate CVV (3-4 digits)
    if not re.match(r'^\d{3,4}$', cvv):
        return jsonify({'error': 'Invalid CVV format'}), 400

    # Validate cardholder name (at least 3 characters)
    if len(cardholder_name.strip()) < 3:
        return jsonify({'error': 'Invalid cardholder name'}), 400

    try:
        # In a real system, you would:
        # 1. Call payment gateway API (Stripe, PayPal, etc.)
        # 2. Store payment transaction record
        # 3. Handle payment failures

        # For this demo, we accept all valid formats
        order.payment_status = True
        # When payment is made, change status from 0 (ordered) to 1 (pending)
        if order.pickup_status == 0:
            order.pickup_status = 1
        db.session.commit()

        return jsonify({
            'message': 'Payment processed successfully',
            'order': order.to_dict(include_items=True, include_store=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Process payment error: {e}")
        return jsonify({'error': 'Failed to process payment'}), 500

