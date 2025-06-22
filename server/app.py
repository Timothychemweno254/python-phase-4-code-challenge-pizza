#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os
from sqlalchemy.exc import IntegrityError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

#=================fetch all restaurants=================
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    result = [
        {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        }
        for restaurant in restaurants
    ]
    return jsonify(result), 200

#======================fetch restaurant by id========================
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    return make_response(restaurant.to_dict(), 200)

#=================delete restaurant by id=================
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return '', 204

#==================get all pizzas==================
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    result = [
        {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        }
        for pizza in pizzas
    ]
    return jsonify(result), 200

#=====================create pizza to restaurant=====================
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    
    if price is None or pizza_id is None or restaurant_id is None:
        return jsonify({"errors": ["Missing required fields"]}), 400

    try:
        
        new_rp = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )

        db.session.add(new_rp)
        db.session.commit()

        
        response_data = {
            "id": new_rp.id,
            "price": new_rp.price,
            "pizza_id": new_rp.pizza_id,
            "restaurant_id": new_rp.restaurant_id,
            "pizza": {
                "id": new_rp.pizza.id,
                "name": new_rp.pizza.name,
                "ingredients": new_rp.pizza.ingredients
            },
            "restaurant": {
                "id": new_rp.restaurant.id,
                "name": new_rp.restaurant.name,
                "address": new_rp.restaurant.address
            }
        }

        return make_response(jsonify(response_data), 201)

    except ValueError as ve:
        db.session.rollback()
        return jsonify({"errors": [str(ve)]}), 400
    except ValueError:
      db.session.rollback()
      return jsonify({"errors": ["validation errors"]}), 400


        
if __name__ == "__main__":
    app.run(port=5555, debug=True)
