
import server.endpoints as ep
import json


TEST_CLIENT = ep.app.test_client()


def test_update_user_info():
    data_to_send = {
        "user_id": 1,
        "data": {
            "username": "new_username",
            "email": "new_email@example.com"
        }
    }

    resp = TEST_CLIENT.put(f'/{ep.UPDATE_USER_INFO}', json=data_to_send)
    resp_json = resp.get_json()
    
    assert isinstance(resp_json, dict)
    assert 'status' in resp_json
    assert resp_json['status'] == 'success'
    assert 'message' in resp_json
    assert resp_json['message'] == f"User {data_to_send['user_id']} info updated"

    test2 = {
        "user_id": 1123,
        "data": {
            "username": "new_username",
            "email": "new_email@example.com"
        }
    }

    resp2 = TEST_CLIENT.put(f'/{ep.UPDATE_USER_INFO}', json=test2)
    resp2_json = resp2.get_json()

    assert 'status' in resp2_json
    assert resp2_json['status'] == 'failure'

def test_UpdateAvailableJobs():
    resp = TEST_CLIENT.put(f'/{ep.UPDATE_AVAILABLE_JOBS}')
    resp_json = resp.get_json()
    
    assert isinstance(resp_json, dict)
    assert 'status' in resp_json
    assert resp_json['status'] == 'success'
    assert 'message' in resp_json
    assert resp_json['message'] == "Jobs updated"


def test_keyword_search_database():
    keyword = "internship"
    resp = TEST_CLIENT.get(f'/{ep.KEYWORD_SEARCH}', json = {"keyword": keyword})
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert "results" in resp_json
    assert isinstance(resp_json["results"], list)
    expected_results = [{"data": {"keywords": ["internship"]},"userid" : 1}]
    assert resp_json['results'] == expected_results

def test_update_job_postings():
    assert True

def test_delete_account():
    assert True

def test_get_user_reports():
    resp = TEST_CLIENT.get(f'/{ep.GET_USER_REPORTS}', json = {"user_id": 1})
    assert resp._status_code == 200
    resp = json.loads(resp.data.decode('utf-8'))
    expected_results =  {"User Reports":  
                [{"user_id": 1, "job_id": 1, "report": "invalid link"},
                  {"user_id": 2, "job_id": 2, "report": "job is closed"},
                  {"user_id": 3, "job_id": 3, "report": "page not found"},]
                  }
    assert resp == expected_results

def test_send_user_report():
    resp = TEST_CLIENT.post(f'/{ep.USER_REPORT}', json={
        'user_id': 1, 'job_id': 1, "report": "TESTING"
    })
    assert resp._status_code == 200;
    resp = json.loads(resp.data.decode('utf-8'))
    expected_results = {"status": "success", "message":
                "User report successfully submitted report"}
                
    assert resp == expected_results  


    resp = TEST_CLIENT.post(f'/{ep.USER_REPORT}', json={
        'user_id': 10, 'job_id': 1, "report": "TESTING"
    })
    assert resp._status_code == 400;
    resp = json.loads(resp.data.decode('utf-8'))
    expected_results =  {"status": "failure", "message":
                "Invalid User ID"}
    assert resp == expected_results 

    resp = TEST_CLIENT.post(f'/{ep.USER_REPORT}', json={
        'user_id': 1, 'job_id': 1, "report": ""
    })
    assert resp._status_code == 400;
    resp = json.loads(resp.data.decode('utf-8'))
    expected_results =  {"status": "failure", "message":
                "Invalid report"}
    assert resp == expected_results 

def test_create_account():
    assert True
    # passed in data for creating an account include:
    # username, password, email
    
    # check each variable aligned with the requirments, provide user_id if successfully create account 
    # if data["username"]:

    # if data["email"]:

    # if data["password"]:

    #create account and provide user_id

def test_login_to_account(): # go to db and check if username/email matches password
    assert True

def test_update_preferences():
    assert True

def test_read_most_recent_jobs():
    assert True

def test_admin_delete_jobs():
    headers = {'Content-Type': 'application/json'}
    data = {"invalid_job": "job_name_to_delete"}  # Provide the expected JSON payload
    resp = TEST_CLIENT.delete(f'/{ep.ADMIN_DELETE_JOBS}', headers=headers, json=data)  # Use the json parameter to include JSON data in the request
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert 'status' in resp_json
    assert resp_json['status'] == 'success'
    assert 'message' in resp_json
    assert resp_json['message'] == "bad job successfully deleted"

def test_admin_delete_past_date():
    headers = {'Content-Type': 'application/json'}
    data = {"invalid_job_date": "past_dates_jobs_to_delete"}  # Provide the expected JSON payload
    resp = TEST_CLIENT.delete(f'/{ep.ADMIN_DELETE_PAST_DATE}', headers=headers, json=data)  # Use the json parameter to include JSON data in the request
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert 'status' in resp_json
    assert resp_json['status'] == 'success'
    assert 'message' in resp_json
    assert resp_json['message'] == "past date jobs successfully deleted"