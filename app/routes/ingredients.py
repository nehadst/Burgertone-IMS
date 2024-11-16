from flask import Blueprint, request, jsonify
from app.models.ingredient import Ingredients
from app import db
from app import ingredients_blueprint

ingredients_blueprit = Blueprint('ingredients', __name__)

#Get all the ingredients

@ingredients_blueprint.route('/', methods = ['GET'])
def get_all_ingredients():
    ingredients = Ingredients.query.all()
    return jsonify([ingredient.__dict__ for ingredient in ingredients])


# Get a single ingredient by ingredient id
@ingredients_blueprint.route('/<int:id>' , methods = ['GET'])
def get_ingredient(id):
    ingredient = Ingredients.query.get(id)
    if not ingredient:
        return jsonify({'message': 'Ingredient not found'}), 404
    return jsonify(ingredient.__dict__)

# Adding a new ingredient
@ingredients_blueprint.route('/', methods = ['POST'])
def add_ingredient():
    data = request.get_jsoN()
    new_ingredient = Ingredients(
        name = data['name'],
        unit = data['unit'],
        quantity = data['quantity'],
        threshold = data['threshold'])
    db.session.add(new_ingredient)
    db.session.commit()

    return jsonify(new_ingredient.__dict__), 201


# Update an ingredient by ingredient id
@ingredients_blueprint.route('/<int:id>', methods = ['PUT'])
def add_ingredient():
    ingredient = Ingredients.query.get(id)
    if not ingredient:
        return jsonify({'message': 'Ingredient not found'}), 404
    data = request.get_jsoN()
    ingredient.name = data['name']
    ingredient.unit = data['unit']
    ingredient.quantity = data['quantity']
    ingredient.threshold = data['threshold']
    db.session.commit()

    return jsonify(ingredient.__dict__)



# Delete an ingredient by ingredient id
@ingredients_blueprint.route('/<int:id>', methods = ['DELETE'])
def delete_ingredient(id):
    ingredient = Ingredients.query.get(id)
    if not ingredient:
        return jsonify({'message': 'Ingredient not found'}), 404
    
    db.session.delete(ingredient)
    db.session.commit()
    return jsonify({'message': 'Ingredient deleted'})
