from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza
from flask_restful import Api, Resource
import os
from sqlalchemy.exc import IntegrityError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

api = Api(app)

db.init_app(app)
migrate = Migrate(app, db)


@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    serialized_restaurants = [restaurant.to_dict() for restaurant in restaurants]
    return jsonify(serialized_restaurants)


@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.filter_by(id=id).one_or_none()
    if restaurant:
        return jsonify(restaurant.to_dict(relationships={"restaurant_pizzas": {"pizza": {}}}))
    else:
        return jsonify({"error": "Restaurant not found"}), 404


@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.filter_by(id=id).one_or_none()
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204
    else:
        return jsonify({"error": "Restaurant not found"}), 404


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    serialized_pizzas = [pizza.to_dict() for pizza in pizzas]
    return jsonify(serialized_pizzas)


@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.json
    try:
        pizza = Pizza.query.filter_by(id=data["pizza_id"]).one()
        restaurant = Restaurant.query.filter_by(id=data["restaurant_id"]).one()

        restaurant_pizza = RestaurantPizza(
            restaurant_id=restaurant.id, pizza_id=pizza.id, price=data["price"]
        )

        db.session.add(restaurant_pizza)
        db.session.commit()

        return jsonify(restaurant_pizza.to_dict(
            relationships={"pizza": {}, "restaurant": {}})), 201
    except KeyError:
        return jsonify({"errors": ["Missing required fields"]}), 400
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": ["Integrity error occurred"]}), 400
    except:
        return jsonify({"errors": ["Pizza or Restaurant not found"]}), 404


if __name__ == "__main__":
    app.run(debug=True)
