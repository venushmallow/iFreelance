import json
import pytest

# for the test cases
def call(client, path, method='GET', body=None):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }

    if method == 'POST':
        response = client.post(path, data=json.dumps(body), headers=headers)
    elif method == 'PUT':
        response = client.put(path, data=json.dumps(body), headers=headers)
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


# test  GET method
# health
@pytest.mark.dependency()
def test_health(client):
    result = call(client, 'health')
    assert result['code'] == 200


#  get all jobs details
@pytest.mark.dependency()
def test_get_all(client):
    result = call(client, 'jobs')
    assert result['code'] == 200
    assert result['json']['data']['jobs'] == [
      {
        "job_id": 1, 
        "price": 40.0, 
        "description": "Design a professional website for your business.",
        "title": "Design Portfolio Website",
        "seller_id": 1
      }, 
      {
        "job_id": 2, 
        "price": 60.5, 
        "description": "Hire my service to wreck any party you want to bail out from but forced to come.",
        "title": "Party Wrecker",
        "seller_id": 1
      }, 
      {
        "job_id": 3, 
        "price": 18.7, 
        "description": "Babysit your children at home.",
        "title": "Babysit Children",
        "seller_id": 1
      }, 
      {
        "job_id": 7, 
        "price": 25.55, 
        "description": "Straight A confirmed.",
        "title": "Do School Homework",
        "seller_id": 1
      }, 
      {
        "job_id": 9, 
        "price": 0.0, 
        "description": "Certified psychologist, free therapy since therapy prices are insane.",
        "title": "Free Therapy",
        "seller_id": 1
      }
    ]


# get specific valid job details 
@pytest.mark.dependency(depends=['test_get_all'])
def test_one_valid(client):
    result = call(client, 'jobs/9')
    assert result['code'] == 200
    assert result['json']['data'] == {
      "job_id": 9,
      "price": 0.0,
      "description": "Certified psychologist, free therapy since therapy prices are insane.",
      "title": "Free Therapy",
      "seller_id": 1
    }


# get specific invalid job details 
@pytest.mark.dependency(depends=['test_get_all'])
def test_one_invalid(client):
    result = call(client, 'jobs/11')
    assert result['code'] == 404
    assert result['json'] == {
        "message": "Job not found."
    }


# test PUT method
# replace existing job details
@pytest.mark.dependency(depends=['test_get_all'])
def test_replace_existing_job(client):
    result = call(client, 'jobs/9', 'PUT', {
        "price": 45.0, 
        "description": "Design a professional website for your business.",
        "title": "Design Portfolio Website",
        "seller_id": 1
    })
    assert result['code'] == 200
    assert result['json']['data'] == {
        "job_id": 9, 
        "price": 45.0, 
        "description": "Design a professional website for your business.",
        "title": "Design Portfolio Website",
        "seller_id": 1
    }


# replace non existing job
@pytest.mark.dependency(depends=['test_get_all'])
def test_replace_nonexisting_job(client):
    result = call(client, 'jobs/11', 'PUT', {
        "price": 45.0, 
        "description": "Design a professional website for your business.",
        "title": "Design Website",
        "seller_id": 1
    })
    assert result['code'] == 404


# test PATCH method
# update job details
@pytest.mark.dependency(depends=['test_get_all'])
def test_update_existing_job(client):
    result = call(client, 'jobs/1', 'PATCH', {
        "price": 45.0
    })
    assert result['code'] == 200
    assert result['json']['data'] == {
        "job_id": 1,
        "price": 45.0, 
        "description": "Design a professional website for your business.",
        "title": "Design Portfolio Website",
        "seller_id": 1
    }


# update nonexisting job
@pytest.mark.dependency(depends=['test_get_all'])
def test_update_nonexisting_job(client):
    result = call(client, 'jobs/11', 'PATCH', {
        "price": 45.0
    })
    assert result['code'] == 404


# # test reserve job
# @pytest.mark.dependency(depends=['test_get_all'])
# def test_reserve_existing_job(client):
#     result = call(client, 'jobs/1', 'PATCH', {
#         "reserve": 1
#     })
#     assert result['code'] == 200
#     assert result['json']['data'] == {
#         "job_id": 1, 
#         "price": 40.0, 
#         "description": "Design a professional website for your business.",
#         "title": "Design Portfolio Website"
#     }

# # reserve the job that has been taken
# @pytest.mark.dependency(depends=['test_get_all', 'test_reserve_existing_job'])
# def test_reserve_existing_job_fail(client):
#     call(client, 'jobs/1', 'PATCH', {
#         "reserve": 1
#     })
#     result = call(client, 'jobs/1', 'PATCH', {
#         "reserve": 1
#     })
#     assert result['code'] == 500
#     assert result['json'] == {
#         "message": "An error occurred updating the job.",
#         "error": "Job is already taken."
#     }

# -------
# unreserve the existing job --- currently will not pass
# @pytest.mark.dependency(depends=['test_get_all', 'test_reserve_existing_job'])
# def test_unreserve_existing_job(client):
#     call(client, 'jobs/1', 'PATCH', {
#         "reserve": 1
#     })
#     result = call(client, 'jobs/1', 'PATCH', {
#         "reserve": -1
#     })
#     assert result['code'] == 200
#     assert result['json']['data'] == {
#         "job_id": 1, 
#         "price": 40.0, 
#         "stock": 1, 
#         "title": "Design Portfolio Website"
#     }

# # reserve job with invalid body
# @pytest.mark.dependency(depends=['test_get_all'])
# def test_reserve_existing_job_fail(client):
#     result = call(client, 'jobs/1', 'PATCH', {
#         "reserve": 1,
#         "price": 10
#     })
#     assert result['code'] == 500


# test POST methods 
# create job with no body (code of response: 500)
@pytest.mark.dependency(depends=['test_get_all'])
def test_create_no_body(client):
    result = call(client, 'jobs', 'POST', {})
    assert result['code'] == 500


# create job with valid body
@pytest.mark.dependency(depends=['test_get_all', 'test_create_no_body'])
def test_create_one_job(client):
    result = call(client, 'jobs', 'POST', {
        "price": 20.0, 
        "description": "Edit video for professional use.",
        "title": "Video Editing",
        "seller_id": 1
    })
    assert result['code'] == 201
    assert result['json']['data'] == {
        "job_id": 28, 
        "price": 20.0, 
        "description": "Edit video for professional use.",
        "title": "Video Editing",
        "seller_id": 1
    }

# test PUT method
# replace the new job details
@pytest.mark.dependency(depends=['test_create_one_job'])
def test_replace_new_job(client):
    call(client, 'jobs', 'POST', {
        "price": 20.0, 
        "description": "Edit video for professional use.",
        "title": "Video Editing",
        "seller_id": 1
    })
    result = call(client, 'jobs/28', 'PUT', {
        "price": 40.0, 
        "description": "Edit video for professional use.",
        "title": "Video Editing",
        "seller_id": 1
    })
    assert result['code'] == 200
    assert result['json']['data'] == {
        "job_id": 28,
        "price": 40.0, 
        "description": "Edit video for professional use.",
        "title": "Video Editing",
        "seller_id": 1
    }


# test update new job
@pytest.mark.dependency(depends=['test_create_one_job'])
def test_update_new_job(client):
    call(client, 'jobs', 'POST', {
        "price": 20.0, 
        "description": "Edit video for professional use.",
        "title": "Video Editing",
        "seller_id": 1
    })
    result = call(client, 'jobs/28', 'PATCH', {
        "price": 40.0
    })
    assert result['code'] == 200
    assert result['json']['data'] == {
        "job_id": 28,
        "price": 40.0, 
        "description": "Edit video for professional use.",
        "title": "Video Editing",
        "seller_id": 1
    }

# test the DELETE method
# delete valid job
@pytest.mark.dependency(depends=['test_get_all'])
def test_delete_job(client):
    result = call(client, 'jobs/7', 'DELETE')
    assert result['code'] == 200
    assert result['json']['data'] == {
        "job_id": 7
    }


# delete invalid job
@pytest.mark.dependency(depends=['test_delete_job'])
def test_deleted_job(client):
    call(client, 'jobs/7', 'DELETE')
    result = call(client, 'jobs/7', 'GET')
    assert result['code'] == 404
    assert result['json']['message'] == "Job not found."
