from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class OnlineAccount(db.Model):
    __tablename__ = "onlineaccount"

    online_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    passwd = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(70), unique=True, nullable=False)
    name = db.Column(db.String(70))

    def set_password(self, password):
        self.passwd = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.passwd, password)

    def to_dict(self):
        return {
            'online_id': self.online_id,
            'email': self.email,
            'name': self.name
        }
