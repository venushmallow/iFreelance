import json
import pytest
import operator


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


def insert_rows(client):
    call(client, 'accounts', 'POST', {
        "user_email": "cposkitt@smu.edu.sg",
        "password": "kopitime",
        "user_phone": "88888888"
    })

    call(client, 'accounts', 'POST', {
        "user_email": "phris@coskitt.com",
        "password": "coffeewaktu",
        "user_phone": "99999999"
    })

    call(client, 'accounts', 'POST', {
        "user_email": "haniel@danley.com",
        "password": "TA",
        "user_phone": "22222222"
    })


@pytest.mark.dependency()
def test_health(client):
    result = call(client, 'health')
    assert result['code'] == 200


@pytest.mark.dependency()
def test_login_successful(client):
    insert_rows(client)
    result = call(client, 'accounts/login', 'POST', {
        "user_email": "cposkitt@smu.edu.sg",
        "password": "kopitime"
    })
    assert result['code'] == 200
    assert result['json']['message']== "Successfully logged in."


@pytest.mark.dependency()
def test_wrongcredentials(client):
    insert_rows(client)
    result = call(client, 'accounts/login', 'POST', {
        "user_email": "cposkitt@smu.edu.sg",
        "password": "thisisnotmypassword"
    })
    assert result['code'] == 403
    assert result['json'] == {
        "message": "Wrong credentials. Please try again."
    }


@pytest.mark.dependency()
def test_account_notfound(client):
    insert_rows(client)
    result = call(client, 'accounts/login', 'POST', {
        "user_email": "hola@smu.edu.sg",
        "password": "kopitime"
    })
    assert result['code'] == 404
    assert result['json'] == {
        "message": "Unable to find account with specified email."
    }


@pytest.mark.dependency()
def test_get_all(client):
    insert_rows(client)
    result = call(client, 'accounts')
    accounts = result['json']['data']['accounts']
    passwords = list(map(operator.itemgetter('password'), accounts))
    assert result['code'] == 200
    assert result['json']['data']['accounts'] == [
      {
        "account_id": 1,
        "password": passwords[0],
        "user_email": "cposkitt@smu.edu.sg",
        "user_phone": "88888888"
      },
      {
        "account_id": 2,
        "password": passwords[1],
        "user_email": "phris@coskitt.com",
        "user_phone": "99999999"
      },
      {
        "account_id": 3,
        "password": passwords[2],
        "user_email": "haniel@danley.com",
        "user_phone": "22222222"
      }
    ]


# This is not a dependency per se (the tests can be
# executed in any order). But if 'test_get_all' does
# not pass, there's no point in running any other
# test, so may as well skip them.

@pytest.mark.dependency(depends=['test_get_all'])
def test_one_valid(client):
    insert_rows(client)
    result = call(client, 'accounts/2')
    password = result['json']['data']['password']
    assert result['code'] == 200
    assert result['json']['data'] == {
        "account_id": 2,
        "user_email": "phris@coskitt.com",
        "password": password,
        "user_phone": "99999999"
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_one_invalid(client):
    insert_rows(client)
    result = call(client, 'accounts/55')
    assert result['code'] == 404
    assert result['json'] == {
        "message": "Account not found."
    }

@pytest.mark.dependency(depends=['test_get_all'])
def test_update_existing_account(client):
    insert_rows(client)
    result = call(client, 'accounts/1', 'PATCH', {
        "password": "new_password",
        "user_phone": "12345678"
    })
    password = result['json']['data']['password']
    assert result['code'] == 200
    assert result['json']['data'] == {
        "account_id": 1,
        "user_email": "cposkitt@smu.edu.sg",
        "password": password,
        "user_phone": "12345678"
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_update_nonexisting_account(client):
    insert_rows(client)
    result = call(client, 'accounts/555', 'PATCH', {
        "user_phone": "23456789"
    })
    assert result['code'] == 404


@pytest.mark.dependency(depends=['test_get_all'])
def test_create_no_body(client):
    insert_rows(client)
    result = call(client, 'accounts', 'POST', {})
    assert result['code'] == 500


@pytest.mark.dependency(depends=['test_get_all', 'test_create_no_body'])
def test_create_one_account(client):
    insert_rows(client)
    result = call(client, 'accounts', 'POST', {
        "user_email": "team3@smu.edu.sg",
        "password": "iFreelance",
        "user_phone": "11111111"
    })
    password = result['json']['data']['password']
    assert result['code'] == 201
    assert result['json']['data'] == {
        "account_id": 4,
        "user_email": "team3@smu.edu.sg",
        "password": password,
        "user_phone": "11111111"
    }


@pytest.mark.dependency(depends=['test_create_one_account'])
def test_update_new_account(client):
    insert_rows(client)
    call(client, 'accounts', 'POST', {
        "user_email": "cs302@smu.edu.sg",
        "password": "project",
        "user_phone": "22222222"
    })
    result = call(client, 'accounts/4', 'PATCH', {
        "user_email": "cs302team3@smu.edu.sg"
    })
    password = result['json']['data']['password']
    assert result['code'] == 200
    assert result['json']['data'] == {
        "account_id": 4,
        "user_email": "cs302team3@smu.edu.sg",
        "password": password,
        "user_phone": "22222222"
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_delete_account(client):
    insert_rows(client)
    result = call(client, 'accounts/2', 'DELETE')
    assert result['code'] == 200
    assert result['json']['data'] == {
        "account_id": 2
    }


@pytest.mark.dependency(depends=['test_delete_account'])
def test_deleted_account(client):
    insert_rows(client)
    call(client, 'accounts/2', 'DELETE')
    result = call(client, 'accounts/2', 'GET')
    assert result['code'] == 404
    assert result['json'] == {
        "message": "Account not found."
    }
