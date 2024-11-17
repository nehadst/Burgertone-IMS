from app import db

class Ingredients(db.Model):
    __tablename__ = "ingredients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float(10, 2), nullable=False)
    threshold = db.Column(db.Float(10, 2), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "unit": self.unit,
            "quantity": self.quantity,
            "threshold": self.threshold
        }
