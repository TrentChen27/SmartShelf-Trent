from app import db

class Address(db.Model):
    __tablename__ = "address"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state = db.Column(db.String(20))
    city = db.Column(db.String(40))
    zipcode = db.Column(db.Integer)
    address_1 = db.Column(db.String(70))
    address_2 = db.Column(db.String(70))

    def to_dict(self):
        return {
            'id': self.id,
            'state': self.state,
            'city': self.city,
            'zipcode': self.zipcode,
            'address_1': self.address_1,
            'address_2': self.address_2
        }
