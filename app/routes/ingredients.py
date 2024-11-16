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