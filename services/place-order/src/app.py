import os
import json
import requests
import amqp_setup
import pika

from flask import Flask, request, jsonify
from flask_cors import CORS

if os.environ.get('stage') == 'production':
    jobs_service_url = os.environ.get('jobs_service_url')
    orders_service_url = os.environ.get('orders_service_url')
    api_key = os.environ.get('api_key')
else:
    jobs_service_url = os.environ.get('jobs_service_url_internal')
    orders_service_url = os.environ.get('orders_service_url_internal')
    api_key = ''

post_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': api_key
    }

app = Flask(__name__)

CORS(app)


@app.route("/health")
def health_check():
    return jsonify(
            {
                "message": "Service is healthy."
            }
    ), 200


@app.route("/place-order", methods=['POST'])
def place_order():

    data = request.get_json()

    # (1) Create the order

    order_response = requests.post(
        orders_service_url + '/orders',
        data=json.dumps({
            "customer_email": data["customer_email"],
            "customer_phone": data["customer_phone"],
            "job_id": data["job_id"],
            "title": data["title"],
            "seller_id": data["seller_id"]
        }),
        headers=post_headers
    )

    # Handle error: if cannot create order record, will not send notification
    if order_response.status_code != 201:
        return jsonify(
            {
                "message": "Unable to place order.",
                "error": "Unable to create order record."
            }
        ), 500

    # (2) Send notification to the AMQP broker

    notification_data = {
        "email": data["notifyemail"],
        "data": data["notiinfo"]
    }

    connection = pika.BlockingConnection(amqp_setup.parameters)

    channel = connection.channel()

    channel.basic_publish(
        exchange=amqp_setup.exchange_name, routing_key="order.new",
        body=json.dumps(notification_data),
        properties=pika.BasicProperties(delivery_mode=2))

    connection.close()

    return jsonify(
        {
            "message": "Order placed.",
            "data": order_response.json()['data']
        }
    ), 200


@app.route("/place-order/update-status", methods=['PATCH'])
def place_order_update_status():
    data = request.get_json()

    # (1) Update the order status

    order_status_response = requests.patch(
        orders_service_url + '/orders/' + str(data['order_id']),
        data=json.dumps({
            "status": data['status']
        }),
        headers=post_headers
    )

    # (2) Send notification to the AMQP broker

    notification_data = {
        "email": data["notifyemail"],
        "data": data["notiinfo"]
    }

    connection = pika.BlockingConnection(amqp_setup.parameters)

    channel = connection.channel()

    channel.basic_publish(
        exchange=amqp_setup.exchange_name, routing_key="order.updated",
        body=json.dumps(notification_data),
        properties=pika.BasicProperties(delivery_mode=2))

    connection.close()

    return jsonify(
        {
            "message": "Order status updated.",
            "data": order_status_response.json()['data']
        }
    ), 200
