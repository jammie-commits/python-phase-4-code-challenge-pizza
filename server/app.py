#!/usr/bin/env python3

import os
from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api
from models import db, Restaurant, RestaurantPizza, Pizza

# Set up base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.getenv("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask app and configure database
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize database and migration
db.init_app(app)
migrate = Migrate(app, db)

# Initialize Flask-RESTful API
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return [restaurant.to_dict(rules=['-restaurant_pizzas']) for restaurant in restaurants], 200

@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def handle_restaurant(id):
    restaurant = Restaurant.query.filter_by(id=id).first()

    if request.method == 'GET':
        if restaurant:
            return restaurant.to_dict(), 200
        return {'error': 'Restaurant not found'}, 404

    if request.method == 'DELETE':
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204
        return {'error': 'Restaurant not found'}, 404

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return [pizza.to_dict(rules=['-restaurant_pizzas']) for pizza in pizzas], 200

@app.route('/restaurant_pizzas', methods=['GET', 'POST'])
def create_new_pizza():
    
    json_data = request.get_json()

    try: 
        new_restaurant_pizza = RestaurantPizza(
            price=json_data.get('price'),
            pizza_id=json_data.get('pizza_id'),
            restaurant_id=json_data.get('restaurant_id')
        )
    except ValueError as e:
        return {'errors': ['validation errors']}, 400

    db.session.add(new_restaurant_pizza)
    db.session.commit()
    return new_restaurant_pizza.to_dict(), 201

if __name__ == "__main__":
    app.run(port=5555, debug=True)
