"""Importing relevant libraries"""
import os
import json
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import timedelta
from flask import (
    Flask,
    jsonify, 
    request,
    g,
    redirect,
    render_template,
    request,
    session
)
stage = os.environ.get('stage')
if stage == 'production':
    jobs_service_url = os.environ.get('jobs_service_url')
    orders_service_url = os.environ.get('orders_service_url')
    place_order_service_url = os.environ.get('place_order_service_url')
    accounts_service_url = os.environ.get('accounts_service_url')
    payment_service_url=os.environ.get('payment_service_url')
    api_key = os.environ.get('api_key')
else:
    jobs_service_url = os.environ.get('jobs_service_url_internal')
    orders_service_url = os.environ.get('orders_service_url_internal')
    place_order_service_url = os.environ.get('place_order_service_url_internal')
    accounts_service_url = os.environ.get('accounts_service_url_internal')
    payment_service_url=os.environ.get('payment_service_url_internal')
    api_key = ''

stripe_service_url=os.environ.get('stripe_service_url')

post_headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': api_key
    }

get_headers={
    'x-api-key': api_key
}
app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size': 100,
                                           'pool_recycle': 280}

db = SQLAlchemy(app)

CORS(app)

app.secret_key = 'somesecretkeythatonlyishouldknow'

class User:
    def __init__(self, account_id, user_email):
        self.account_id = account_id
        self.user_email = user_email

    def __repr__(self):
        return f'<User: {self.user_email}>'


# login session
@app.before_request
def before_request():
    g.user = None
    g.stage = stage
    g.jobs_url = os.environ.get('jobs_service_url')
    g.orders_url = os.environ.get('orders_service_url')
    g.accounts_url = os.environ.get('accounts_service_url')
    g.stripe_url = stripe_service_url + '/checkout'

    if 'user_id' in session:
        url = accounts_service_url + "/accounts/" + str(session["user_id"]) 
        user = requests.get(url, headers=get_headers).json()
        g.user = User(account_id = user['data']['account_id'], user_email = user['data']['user_email'])
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)


@app.route("/health")
def health_check():
    return jsonify(
            {
                "message": "Web UI is healthy."
            }
    ), 200


# render to the login page
@app.route("/login_signup")
def render_login_page():
    return render_template("login-signup.html")


# render to the home page
@app.route("/homepage")
def go_to_home_page():
    return render_template("index.html")


# render to the job page
@app.route("/addjobpage", methods=['GET', 'POST'])
def go_to_addjob_page():
    return render_template("addJob.html")

# render to the job page
@app.route("/jobpage", methods=['GET', 'POST'])
def go_to_job_page():
    return render_template("jobs.html")


# render to the order page
@app.route("/buyer_page", methods=['GET', 'POST'])
def render_buyer_page():
    return render_template("orders-buyer.html")


# render to the order page
@app.route("/seller_page", methods=['GET', 'POST'])
def render_seller_page():
    return render_template("orders-seller.html")


# post singup info to account service
@app.route("/signup", methods=['GET', 'POST'])  
def render_signup_page():
    try:
        user_email = request.form.get('user_email')
        password = request.form.get('password')
        user_phone = request.form.get('user_phone')

        signup_response = requests.post(
            accounts_service_url + '/accounts',
            data = json.dumps({   
                "user_phone": str(user_phone),   
                "user_email": str(user_email),
                "password": str(password)
            }),
            headers=post_headers
        )
        return render_template("login-signup.html")
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred creating the account.",
                "error": str(e)
            }
        ), 500


# post login info to account service
@app.route("/login", methods=['POST'])  
def render_index_page():
    try:
        session.pop('user_id', None)
        user_email = request.form.get('user_email')
        password = request.form.get('password')

        login_response = requests.post(
            accounts_service_url + '/accounts/login',
            data = json.dumps({         
                "user_email": user_email,
                "password": password
            }),
            headers=post_headers
       )
        userinfo = login_response.json()
        # if login successful
        if str(login_response) == "<Response [200]>":
            session['user_id'] = userinfo['data']['account_id']
            g.user = User(account_id = userinfo['data']['account_id'], 
                        user_email = userinfo['data']['user_email'])
            # redirect to home page
            return render_template("index.html")
        else:  
            # redirect login page
            return render_template("login-signup.html")

    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred in login.",
                "error": str(e)
            }
        ), 500


# post job data from jobpage -> placeorder 
@app.route("/placeorderpage", methods=['POST'])  
def render_place_order_page():
    try:
        job_id = request.form.get('job_id')
        title = request.form.get('title')
        seller_id = request.form.get('seller_id')

        return render_template("placeorder.html", 
            job_id=int(job_id), title = str(title),
            seller_id=seller_id)
        
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred to render place-order page.",
                "error": str(e)
            }
        ), 500


# post order data to place order service
@app.route("/placeorder", methods=['POST'])  
def place_order_and_render_order_spage():
    try:
        job_id = request.form.get('job_id')
        title = request.form.get('title')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        seller_id = request.form.get('seller_id')
        #fetch seller email
        account_url = accounts_service_url + '/accounts/'+ str(seller_id)
        account_data = requests.get(account_url, headers=get_headers).json()
        # notification info
        notiinfo = "Customer " + customer_email +" placed an order on Your job " + title

        place_order_response = requests.post(
            place_order_service_url + '/place-order',
            data = json.dumps({         
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "job_id": int(job_id),
                "title": title,
                "seller_id": seller_id,
                "notiinfo": notiinfo,
                "notifyemail": account_data['data']['user_email']
            }),
            headers=post_headers
        )
        return render_template("orders-buyer.html")
        
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred when placing the order",
                "error": str(e)
            }
        ), 500


@app.route("/updateorderpage", methods=['POST'])
def render_updated_order_page():         
    order_id = request.form.get('order_id') 
    status =  request.form.get('status') 
    customer_email =  request.form.get('customer_email') 
    customer_phone =  request.form.get('customer_phone') 
    title =  request.form.get('title') 

    # if is making payment, it will send the payment data to payment service
    if status == 'NEW' or status == 'COMPLETED':
        # status = "PAID"
        # notify_email = account_data['data']['user_email']
        order_url = orders_service_url + '/orders/'+ str(order_id)
        order_data = requests.get(order_url, headers=get_headers).json()

        job_id = order_data['data']['job_id']
        job_url = jobs_service_url + '/jobs/'+ str(job_id)
        job_data = requests.get(job_url, headers=get_headers).json()
        price = int(job_data['data']['price'] * 100 * 0.5)

        if status == 'NEW':
            notiinfo = "Customer " + order_data['data']["customer_email"] +" made deposit on " + order_data['data']['title']
        elif status == 'COMPLETED':
            notiinfo = "Customer " + order_data['data']["customer_email"] +" made payment on " + order_data['data']['title']

        if send_data_to_payment_service(price, order_id) == True:
            return render_template("orders-buyer.html")
        else: 
            return jsonify({
                "error": "Error occur in sending payment info"
            })

    else:
        return render_template("updateorder.html", order_id=order_id, 
        status=status,customer_email = customer_email, 
        customer_phone = customer_phone, title = title)


@app.route("/updateorder", methods=['POST'])
def update_orders_render_order_page():
    # retrieve the data from updateorder 
    order_id = request.form.get('order_id')
    status =  request.form.get('status')

    order_url = orders_service_url + '/orders/'+ str(order_id)
    order_data = requests.get(order_url, headers=get_headers).json()

    account_url = accounts_service_url + '/accounts/'+ str(order_data['data']["seller_id"])
    account_data = requests.get(account_url, headers=get_headers).json()

    if status == 'PENDING':
        status = "NEW"
        notify_email = order_data['data']["customer_email"]
        notiinfo = "Seller " + account_data['data']['user_email'] +" accepted your order " + order_data['data']['title']

    elif status == 'PAID':
        status = "COMPLETED"
        # customer_email
        notify_email = order_data['data']["customer_email"]
        notiinfo = "Seller " + account_data['data']['user_email'] +" completed your order " + order_data['data']['title']

    return update_order_status(order_id, status, notify_email, notiinfo)


# update_order_status 
def update_order_status(order_id, status, notify_email, notiinfo):
    try:
        order_response = requests.patch(
                place_order_service_url + '/place-order/update-status',
                data=json.dumps({
                    "order_id": int(order_id),
                    "status": status,
                    "notifyemail": notify_email,
                    "notiinfo": notiinfo
                }),
                headers=post_headers
            )
        # return to the UI
        return render_template("orders-buyer.html")
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred updating the order.",
                "error": str(e)
            }
        ), 500


# send payment data to payment service
def send_data_to_payment_service(price, order_id):
    try:
        payment_response = requests.post(
            payment_service_url,
            data = json.dumps({
                "username": str(g.user.account_id),
                "email": g.user.user_email,
                "amount": price,
                "order_id": str(order_id)
            }),
            headers=post_headers
        )
        if str(payment_response) == "<Response [200]>":
            return True
        else:
            return False
    except Exception as e:
        return jsonify({
            "message": "An error occurred in send data to Payment service.",
            "error": str(e)
        }), 500


# post job data to job service
@app.route("/addjob", methods=['POST'])  
def add_job_render_jobs_page():
    
    title = request.form.get('title')
    price = request.form.get('price')
    description = request.form.get('description')
    
    try:
        job_response = requests.post(
            jobs_service_url + '/jobs',
            data = json.dumps({
                "title": title,
                "price": float(price),
                "description": description,
                "seller_id": g.user.account_id
            }),
            headers=post_headers
        )
        return render_template("orders-buyer.html")

    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred get the job info.",
                "error": str(e)
            }
        ), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
