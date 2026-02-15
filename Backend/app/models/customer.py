from app import db

class Customer(db.Model):
    __tablename__ = "customer"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    online_id = db.Column(db.Integer, db.ForeignKey('onlineaccount.online_id'))
    kind = db.Column(db.Integer)  # 0=home, 1=biz
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'online_id': self.online_id,
            'kind': self.kind,
            'address_id': self.address_id
        }


class Home(db.Model):
    __tablename__ = "home"

    id = db.Column(db.Integer, db.ForeignKey('customer.id'), primary_key=True)
    marriage_status = db.Column(db.Integer)  # 0=single, 1=married, 2=divorced, 3=widowed
    gender = db.Column(db.String(20))
    age = db.Column(db.Integer)
    income = db.Column(db.BigInteger)
    sales_id = db.Column(db.Integer, db.ForeignKey('salesperson.employee_id'))

    def to_dict(self):
        return {
            'id': self.id,
            'marriage_status': self.marriage_status,
            'gender': self.gender,
            'age': self.age,
            'income': self.income,
            'sales_id': self.sales_id
        }


class Business(db.Model):
    __tablename__ = "business"

    id = db.Column(db.Integer, db.ForeignKey('customer.id'), primary_key=True)
    company_name = db.Column(db.String(140))
    category = db.Column(db.String(70))
    gross_income = db.Column(db.BigInteger)
    sales_id = db.Column(db.Integer, db.ForeignKey('salesperson.employee_id'))

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'category': self.category,
            'gross_income': self.gross_income,
            'sales_id': self.sales_id
        }
