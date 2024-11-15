from app import db

class Ingredients(db.Model):
    id = db.Column(d.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float(10,2), nullable=False)
    threshold = db.Column(db.Float(10,2), nullable=False)

    def __repr__(self):
        return f'<Ingredient {self.name}>'
