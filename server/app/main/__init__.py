import json

from flask import Blueprint, jsonify, request

from app.database import DB
from app.models.recipe import Recipe

bp = Blueprint('main', __name__)


def buildQueryWithIngredients(ingredients):
    r = []
    for el in ingredients:
        r.append(
            {
                'ingredients': {
                    '$elemMatch': {
                        '$regex': '.*' + el + '.*'
                    }
                }
            }
        )
    query = { '$and': r }
    return query


@bp.route('/recipe', methods=['POST'])
def insert():
    newRecipe = Recipe(
        request.json['title'],
        request.json['introduction'],
        request.json['url'],
        request.json['diners'],
        request.json['duration'],
        request.json['difficulty'],
        request.json['ingredients'],
        request.json['steps'],
    )
    r = list(DB.find('recipes', {'url': newRecipe.url}))
    if len(r) == 0:
        DB.insert('recipes', newRecipe.json())
        return ('Element added', 204)
    else:
        return ('The element already exists', 409)

@bp.route('/recipe', methods=['GET'])
def find():
    l = list(DB.find('recipes', request.json))
    return {'content': l}

@bp.route('/recipe', methods=['DELETE'])
def delete():
    return DB.remove('recipes', request.json)

@bp.route('/recipe-for-ingredients', methods=['GET'])
def findRecipeForIngredients():
    listOfIngredients = request.json['ingredients']
    l = list(DB.find('recipes', buildQueryWithIngredients(listOfIngredients)))
    return {'content': l}
