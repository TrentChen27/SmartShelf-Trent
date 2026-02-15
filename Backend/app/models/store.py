from app import db

class Store(db.Model):
    __tablename__ = "store"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(70), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))

    # Relationships
    address = db.relationship('Address', foreign_keys=[address_id], lazy='joined')

    def to_dict(self, include_address=False):
        data = {
            'id': self.id,
            'name': self.name,
            'region_id': self.region_id,
            'manager_id': self.manager_id
        }
        if include_address and self.address:
            data['address'] = self.address.to_dict()
        return data
