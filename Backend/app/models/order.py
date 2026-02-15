from app import db
from datetime import datetime
import pytz

# US Eastern timezone
EASTERN_TZ = pytz.timezone('America/New_York')

def get_eastern_time():
    """Get current time in US Eastern timezone"""
    return datetime.now(EASTERN_TZ)

class Orders(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    sales_id = db.Column(db.Integer, db.ForeignKey('salesperson.employee_id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=get_eastern_time)
    pickup_date = db.Column(db.DateTime, nullable=False, default=get_eastern_time)
    total_amount = db.Column(db.BigInteger)
    payment_status = db.Column(db.Boolean, default=False)
    pickup_status = db.Column(db.Integer, default=0)  # 0=ordered (unpaid), 1=pending (paid), 2=complete (picked up), 3=cancelled

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True)
    store = db.relationship('Store', backref='orders', lazy=True)
    customer = db.relationship('Customer', backref='orders', lazy=True)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True)
    store = db.relationship('Store', backref='orders', lazy=True)
    customer = db.relationship('Customer', backref='orders', lazy=True)

    def to_dict(self, include_items=False, include_store=False, include_customer_name=False, include_sales_name=False):
        # Ensure order_date has timezone info
        order_date_str = None
        if self.order_date:
            # If order_date is naive (no timezone), assume it's Eastern time
            if self.order_date.tzinfo is None:
                order_date_et = EASTERN_TZ.localize(self.order_date)
            else:
                order_date_et = self.order_date.astimezone(EASTERN_TZ)
            order_date_str = order_date_et.strftime('%Y-%m-%d %H:%M:%S ET')

        # Ensure pickup_date has timezone info
        pickup_date_str = None
        if self.pickup_date:
            # If pickup_date is naive (no timezone), assume it's Eastern time
            if self.pickup_date.tzinfo is None:
                pickup_date_et = EASTERN_TZ.localize(self.pickup_date)
            else:
                pickup_date_et = self.pickup_date.astimezone(EASTERN_TZ)
            pickup_date_str = pickup_date_et.strftime('%Y-%m-%d %H:%M:%S ET')

        data = {
            'id': self.id,
            'customer_id': self.customer_id,
            'store_id': self.store_id,
            'sales_id': self.sales_id,
            'order_date': order_date_str,
            'pickup_date': pickup_date_str,
            'total_amount': self.total_amount,
            'payment_status': self.payment_status,
            'pickup_status': self.pickup_status
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        if include_store and self.store:
            data['store'] = {
                'id': self.store.id,
                'name': self.store.name
            }
        if include_customer_name and self.customer:
            from app.models.account import OnlineAccount
            from app.models.address import Address
            account = OnlineAccount.query.get(self.customer.online_id)
            data['customer_name'] = account.name if account else 'Unknown'
            # Include customer address
            if self.customer.address_id:
                address = Address.query.get(self.customer.address_id)
                if address:
                    data['customer_address'] = address.to_dict()
        if include_sales_name and self.sales_id:
            from app.models.employee import Employee
            from app.models.account import OnlineAccount
            employee = Employee.query.get(self.sales_id)
            if employee:
                account = OnlineAccount.query.get(employee.online_id)
                data['sales_name'] = account.name if account else 'Unknown'
            else:
                data['sales_name'] = 'Unknown'
        return data


class OrderItem(db.Model):
    __tablename__ = "orderitem"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sub_price = db.Column(db.BigInteger, nullable=False)

    # Relationships
    product = db.relationship('Product', backref='order_items', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'sub_price': self.sub_price,
            'product': self.product.to_dict() if self.product else None
        }
