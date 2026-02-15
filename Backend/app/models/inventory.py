from app import db

class StoreInventory(db.Model):
    __tablename__ = "storeinventory"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint('store_id', 'product_id'),)

    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'product_id': self.product_id,
            'stock': self.stock
        }
