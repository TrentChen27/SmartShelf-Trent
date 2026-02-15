from app import db

class Employee(db.Model):
    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    online_id = db.Column(db.Integer, db.ForeignKey('onlineaccount.online_id'))
    job_title = db.Column(db.String(70))
    salary = db.Column(db.BigInteger)

    def to_dict(self):
        return {
            'id': self.id,
            'online_id': self.online_id,
            'job_title': self.job_title,
            'salary': self.salary
        }
