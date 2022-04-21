"""Importing relevant libraries"""
import os

from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


app = Flask(__name__)
if os.environ.get('db_conn'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('db_conn')+'/order'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = None
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size': 100,
                                           'pool_recycle': 280}

db = SQLAlchemy(app)

CORS(app)


class Order(db.Model):
    """Define a class Order as a shortcut"""
    __tablename__ = 'order'

    order_id = db.Column(db.Integer, primary_key=True)
    customer_email = db.Column(db.String(64), nullable=False)
    customer_phone = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    job_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(64), nullable=False)

    def json(self):
        dto = {
            "order_id": self.order_id,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "seller_id": self.seller_id,
            "status": self.status,
            "created": self.created,
            "job_id": self.job_id,
            "title": self.title
        }

        return dto


@app.route("/health")
def health_check():
    return jsonify(
            {
                "message": "Service is healthy."
            }
    ), 200


@app.route("/orders")
def get_all():
    order_list = Order.query.all()
    if len(order_list) != 0:
        return jsonify(
            {
                "data": {
                    "orders": [order.json() for order in order_list]
                }
            }
        ), 200
    return jsonify(
        {
            "message": "There are no orders."
        }
    ), 404


@app.route("/orders/<int:order_id>")
def find_by_id(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    if order:
        return jsonify(
            {
                "data": order.json()
            }
        ), 200
    return jsonify(
        {
            "message": "Order not found."
        }
    ), 404


# filter orders based on customer email (Buyer view)
@app.route("/orders/buyer/<email>")
def find_by_customer_email(email):
    order_list = Order.query.filter_by(customer_email=email).all()
    if len(order_list) != 0:
        return jsonify(
            {
                "data": {
                    "orders": [order.json() for order in order_list]
                }
            }
        ), 200
    return jsonify(
        {
            "message": "Order not found."
        }
    ), 404


# filter orders based on seller id (Seller view)
@app.route("/orders/seller/<int:account_id>")
def find_by_sellerid(account_id):
    order_list = Order.query.filter_by(seller_id=account_id).all()
    if len(order_list) != 0:
        return jsonify(
            {
                "data": {
                    "orders": [order.json() for order in order_list]
                }
            }
        ), 200
    return jsonify(
        {
            "message": "Order not found."
        }
    ), 404


@app.route("/orders", methods=['POST'])
def new_order():
    try:
        customer_email = request.json.get('customer_email')
        customer_phone = request.json.get('customer_phone')
        seller_id = request.json.get('seller_id')
        job_id = request.json.get('job_id')
        title = request.json.get('title')

        order = Order(customer_email=customer_email,
                      customer_phone=customer_phone,
                      seller_id=seller_id,
                      status='PENDING',
                      job_id=job_id,
                      title=title)

        db.session.add(order)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred creating the order.",
                "error": str(e)
            }
        ), 500

    return jsonify(
        {
            "data": order.json()
        }
    ), 201


@app.route("/orders/<int:order_id>", methods=['PATCH'])
def update_order(order_id):
    order = Order.query.with_for_update(of=Order)\
                 .filter_by(order_id=order_id).first()
    if order is not None:
        data = request.get_json()
        if 'status' in data.keys():
            if order.status == "COMPLETED":
                if data['status'] == "PAID":
                    order.status = "END"
                else:
                    order.status = data['status']
            else:
                order.status = data['status']
        try:
            db.session.commit()
        except Exception as e:
            return jsonify(
                {
                    "message": "An error occurred updating the order.",
                    "error": str(e)
                }
            ), 500
        return jsonify(
            {
                "data": order.json()
            }
        )
    return jsonify(
        {
            "data": {
                "order_id": order_id
            },
            "message": "Order not found."
        }
    ), 404
