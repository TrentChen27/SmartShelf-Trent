from app import db

class Region(db.Model):
    __tablename__ = "region"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region_name = db.Column(db.String(70), nullable=False)
    region_manager = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'region_name': self.region_name,
            'region_manager': self.region_manager
        }
