"""Importing relevant libraries"""
import os

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


app = Flask(__name__)

base_url = os.environ.get('services_accounts_url_internal')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('db_conn') + '/account'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size': 100,
                                           'pool_recycle': 280}

db = SQLAlchemy(app)

CORS(app)


class Account(db.Model):
    __tablename__ = 'account'

    account_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_phone = db.Column(db.Integer, nullable=False)

    def __init__(self, user_email, password, user_phone):
        self.user_email = user_email
        self.password = password
        self.user_phone = user_phone

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "user_email": self.user_email,
            "password": self.password,
            "user_phone": self.user_phone
        }

    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)


@app.route("/health")
def health_check():
    return jsonify(
            {
                "message": "Service is healthy."
            }
    ), 200


@app.route("/accounts/login", methods=['POST'])
def login():
    data = request.get_json()
    # Obtain email and phone
    if not data and "user_email" not in data \
       and "password" not in data:
        return jsonify(
            {
                "message": "Incomplete body."
            }
        ), 400

    email = data['user_email']
    password = data['password']

    account = Account.query.filter_by(user_email=email).first()

    if account:
        if account.verify_password(password):
            return jsonify({
                "message": "Successfully logged in.",
                "data": {
                    "account_id": account.account_id,
                    "user_email": account.user_email,
                    "user_phone": account.user_phone
                }
            }), 200
    else:
        return jsonify({
            "message": "Unable to find account with specified email."
        }), 404

    return jsonify({
        "message": "Wrong credentials. Please try again."
    }), 403


@app.route("/accounts")
def get_all():
    account_list = Account.query.all()
    if len(account_list) != 0:
        return jsonify(
            {
                "data": {
                    "accounts": [account.to_dict() for account in account_list]
                }
            }
        ), 200
    return jsonify(
        {
            "message": "There are no accounts."
        }
    ), 404


@app.route("/accounts/<int:account_id>")
def find_by_id(account_id):
    account = Account.query.filter_by(account_id=account_id).first()
    if account:
        return jsonify(
            {
                "data": account.to_dict()
            }
        ), 200
    return jsonify(
        {
            "message": "Account not found."
        }
    ), 404


@app.route("/accounts", methods=['POST'])
def new_account():
    try:
        data = request.get_json()
        password = data['password']
        data['password'] = generate_password_hash(password, "sha256")
        account = Account(**data)
        db.session.add(account)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred creating the account.",
                "error": str(e)
            }
        ), 500

    return jsonify(
        {
            "data": account.to_dict()
        }
    ), 201


@app.route("/accounts/<int:account_id>", methods=['PATCH'])
def update_account(account_id):
    account = Account.query.with_for_update(of=Account)\
               .filter_by(account_id=account_id).first()
    if account is None:
        return jsonify(
            {
                "data": {
                    "account_id": account_id
                },
                "message": "Account not found."
            }
        ), 404
    data = request.get_json()
    if 'user_email' in data.keys():
        account.user_email = data['user_email']
    if 'password' in data.keys():
        account.password = generate_password_hash(data['password'], 'md5')
    if 'user_phone' in data.keys():
        account.user_phone = data['user_phone']
    try:
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred updating the account.",
                "error": str(e)
            }
        ), 500
    return jsonify(
        {
            "data": account.to_dict()
        }
    )


@app.route("/accounts/<int:account_id>", methods=['DELETE'])
def delete_account(account_id):
    account = Account.query.filter_by(account_id=account_id).first()
    if account is not None:
        try:
            db.session.delete(account)
            db.session.commit()
        except Exception as e:
            return jsonify(
                {
                    "message": "An error occurred deleting the account.",
                    "error": str(e)
                }
            ), 500
        return jsonify(
            {
                "data": {
                    "account_id": account_id
                }
            }
        ), 200
    return jsonify(
        {
            "data": {
                "account_id": account_id
            },
            "message": "account not found."
        }
    ), 404
