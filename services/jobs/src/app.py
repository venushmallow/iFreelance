"""Importing relevant libraries"""
import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


app = Flask(__name__)
if os.environ.get('db_conn'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('db_conn') + '/job'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = None
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size': 100,
                                           'pool_recycle': 280}

db = SQLAlchemy(app)

CORS(app)


class Job(db.Model):
    __tablename__ = 'job'

    job_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)

    def __init__(self, title, description, price, seller_id):
        self.title = title
        self.description = description
        self.price = price
        self.seller_id = seller_id

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "seller_id": self.seller_id
        }


@app.route("/health")
def health_check():
    return jsonify(
        {
            "message": "I love kopi and I love teh :-) ~"
        }
    ), 200


@app.route("/jobs")
def get_all():
    job_list = Job.query.all()
    if len(job_list) != 0:
        return jsonify(
            {
                "data": {
                    "jobs": [job.to_dict() for job in job_list]
                }
            }
        ), 200
    return jsonify(
        {
            "message": "There are no jobs."
        }
    ), 404


@app.route("/jobs/<int:job_id>")
def find_by_id(job_id):
    job = Job.query.filter_by(job_id=job_id).first()
    if job:
        return jsonify(
            {
                "data": job.to_dict()
            }
        ), 200
    return jsonify(
        {
            "message": "Job not found."
        }
    ), 404


# filter out job which is posted by login user himself
@app.route("/jobs/exclude/<int:seller_id>")
def get_job(seller_id):

    # if there is no jobs related to the seller_id
    job_list = Job.query.filter_by(seller_id=seller_id).all()
    if len(job_list) == 0:
        return get_all()

    job_list = Job.query.all()
    if len(job_list) != 0:
        result = []
        for job in job_list:
            if job.seller_id != seller_id:
                result.append(job)

        return jsonify(
            {
                "data": {
                    "jobs": [job.to_dict() for job in result]
                }
            }
        ), 200
    return jsonify(
        {
            "message": "There are no jobs."
        }
    ), 404


@app.route("/jobs", methods=['POST'])
def new_job():
    try:
        data = request.get_json()
        job = Job(**data)
        db.session.add(job)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred creating the job.",
                "error": str(e)
            }
        ), 500

    return jsonify(
        {
            "data": job.to_dict()
        }
    ), 201


@app.route("/jobs/<int:job_id>", methods=['PUT'])
def replace_job(job_id):
    job = Job.query.filter_by(job_id=job_id).first()
    if job:
        try:
            job.price = request.json.get('price', job.price)
            job.title = request.json.get('title', job.title)
            job.description = request.json.get('description', job.description)
            job.seller_id = request.json.get('seller_id', job.seller_id)
            db.session.commit()
        except Exception as e:
            return jsonify(
                {
                    "message": "An error occurred replacing the job.",
                    "error": str(e)
                }
            ), 500

        return jsonify(
            {
                "data": job.to_dict()
            }
        ), 200
    else:
        return jsonify(
            {
                "data": {
                    "job_id": job_id
                },
                "message": "Job not found."
            },
        ), 404


@app.route("/jobs/<int:job_id>", methods=['PATCH'])
def update_job(job_id):
    job = Job.query.with_for_update(of=Job)\
               .filter_by(job_id=job_id).first()
    if job is None:
        return jsonify(
            {
                "data": {
                    "job_id": job_id
                },
                "message": "Job not found."
            }
        ), 404
    data = request.get_json()
    if 'price' in data.keys():
        job.price = data['price']
    if 'description' in data.keys():
        job.description = data['description']
    if 'title' in data.keys():
        job.title = data['title']
    if 'seller_id' in data.keys():
        job.seller_id = data['seller_id']
    try:
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred updating the job.",
                "error": str(e)
            }
        ), 500
    return jsonify(
        {
            "data": job.to_dict()
        }
    )


@app.route("/jobs/<int:job_id>", methods=['DELETE'])
def delete_job(job_id):
    job = Job.query.filter_by(job_id=job_id).first()
    if job:
        try:
            db.session.delete(job)
            db.session.commit()
        except Exception as e:
            return jsonify(
                {
                    "message": "An error occurred deleting the job.",
                    "error": str(e)
                }
            ), 500

        return jsonify(
            {
                "data": {
                    "job_id": job_id
                }
            }
        ), 200

    else:
        return jsonify(
            {
                "data": {
                    "job_id": job_id
                },
                "message": "Job not found."
            }
        ), 404
