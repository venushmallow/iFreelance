import json
import pytest


def call(client, path, method='GET', body=None):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }

    if method == 'POST':
        response = client.post(path, data=json.dumps(body), headers=headers)
    elif method == 'PATCH':
        response = client.patch(path, data=json.dumps(body), headers=headers)
    elif method == 'DELETE':
        response = client.delete(path)
    else:
        response = client.get(path)

    return {
        "json": json.loads(response.data.decode('utf-8')),
        "code": response.status_code
    }

# Test GET methods
@pytest.mark.dependency()
def test_health(client):
    result = call(client, 'health')
    assert result['code'] == 200


# test to get all order details
@pytest.mark.dependency()
def test_get_all(client):
    result = call(client, 'orders')
    assert result['code'] == 200
    assert result['json']['data']['orders'] == [
      {
        "created": "Tue, 10 Aug 2021 00:00:00 GMT", 
        "customer_email": "cposkitt@smu.edu.sg", 
        "customer_phone": 88888888, 
        "seller_id": 1,
        "order_id": 5, 
        "job_id": 2,
        "title": "Party Wrecker",
        "status": "PENDING"
      }, 
      {
        "created": "Tue, 10 Aug 2021 00:00:00 GMT", 
        "customer_email": "phris@coskitt.com", 
        "customer_phone": 99999999, 
        "seller_id": 1,
        "order_id": 6, 
        "job_id": 9,
        "title": "Free Therapy",
        "status": "PENDING"
      }
    ]


# The tests can be executed in any order. 
# But if 'test_get_all' does not pass, will skip other tests

# test to get sepcific order detail
@pytest.mark.dependency(depends=['test_get_all'])
def test_one_valid(client):
    result = call(client, 'orders/6')
    assert result['code'] == 200
    assert result['json']['data'] == {
        "created": "Tue, 10 Aug 2021 00:00:00 GMT", 
        "customer_email": "phris@coskitt.com", 
        "customer_phone": 99999999, 
        "seller_id": 1,
        "order_id": 6, 
        "job_id": 9,
        "title": "Free Therapy",
        "status": "PENDING"
    }


# test to get non-existing order detail
@pytest.mark.dependency(depends=['test_get_all'])
def test_one_invalid(client):
    result = call(client, 'orders/2')
    assert result['code'] == 404
    assert result['json'] == {
        "message": "Order not found."
    }


# Test PATCH method
# update existing order
@pytest.mark.dependency(depends=['test_get_all'])
def test_update_existing_order(client):
    result = call(client, 'orders/6', 'PATCH', {
        "status": "CANCELLED"
    })
    assert result['code'] == 200
    assert result['json']['data']['customer_email'] == "phris@coskitt.com"
    assert result['json']['data']['customer_phone'] == 99999999
    assert result['json']['data']['seller_id'] == 1
    assert result['json']['data']['order_id'] == 6
    assert result['json']['data']['status'] == 'CANCELLED'
    assert result['json']['data']['job_id'] == 9
    assert result['json']['data']['title'] == 'Free Therapy'



# update non-existing order
@pytest.mark.dependency(depends=['test_get_all'])
def test_update_nonexisting_order(client):
    result = call(client, 'orders/7', 'PATCH', {
        "status": "CANCELLED"
    })
    assert result['code'] == 404


# Test POST method
# test create new order with invalid request body
@pytest.mark.dependency(depends=['test_get_all'])
def test_create_no_body(client):
    result = call(client, 'orders', 'POST', {})
    assert result['code'] == 500


# test create new order with valid request body
@pytest.mark.dependency(depends=['test_get_all', 'test_create_no_body'])
def test_create_one_order(client):
    result = call(client, 'orders', 'POST', {
        "customer_email": "haniel@danley.com",
        "customer_phone": 77777777, 
        "seller_id": 1,
        "job_id": 1, 
        "title": "Design Project Website"
    })
    assert result['code'] == 201
    assert result['json']['data']['customer_email'] == "haniel@danley.com"
    assert result['json']['data']['customer_phone'] == 77777777
    assert result['json']['data']['seller_id'] == 1
    assert result['json']['data']['order_id'] == 7
    assert result['json']['data']['status'] == 'PENDING'
    assert result['json']['data']['job_id'] == 1
    assert result['json']['data']['title'] == "Design Project Website"



# test update new order
@pytest.mark.dependency(depends=['test_create_one_order'])
def test_update_new_order(client):
    call(client, 'orders', 'POST', {
        "customer_email": "haniel@danley.com",
        "customer_phone": 77777777, 
        "seller_id": 1,
        "job_id": 1, 
        "title": "Design Project Website"
    })
    result = call(client, 'orders/7', 'PATCH', {
        "status": "CANCELLED"
    })
    assert result['code'] == 200
    assert result['json']['data']['customer_email'] == "haniel@danley.com"
    assert result['json']['data']['order_id'] == 7
    assert result['json']['data']['status'] == 'CANCELLED'
    assert result['json']['data']['job_id'] == 1
    assert result['json']['data']['title'] == "Design Project Website"