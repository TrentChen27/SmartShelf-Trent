from app import db

class SalesPerson(db.Model):
    __tablename__ = "salesperson"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, unique=True)

    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'employee_id': self.employee_id
        }
