from app import db

class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(140), nullable=False)
    price = db.Column(db.BigInteger, nullable=False)  # Price in cents
    kind = db.Column(db.String(70))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'price': self.price,
            'kind': self.kind,
            'description': self.description,
            'image_url': self.image_url
        }
