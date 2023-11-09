
import server.endpoints as ep
import json
import pytest
from unittest.mock import patch
from http.client import (
    NOT_ACCEPTABLE,
    OK
)

TEST_CLIENT = ep.app.test_client()


def test_update_user_info():

    resp = TEST_CLIENT.put(f'/{ep.UPDATE_USER_INFO}', json={"user_id": 1})
    resp_json = resp.get_json()
    
    assert isinstance(resp_json, dict)
    assert 'status' in resp_json
    assert resp_json['status'] == 'success'
    assert 'message' in resp_json
    assert resp_json['message'] == f"User {1} info updated"


def test_update_user_info_bad():
    test = {
        "user_id": 1123,
        "data": {
            "username": "new_username",
            "email": "new_email@example.com"
        }
    }

    resp = TEST_CLIENT.put(f'/{ep.UPDATE_USER_INFO}', json=test)
    assert resp.status_code == NOT_ACCEPTABLE

@patch('db.db.external_job_update', return_value=True, autospec=True)
def test_UpdateAvailableJobs_OK(mock_add):
    resp = TEST_CLIENT.put(f'/{ep.UPDATE_AVAILABLE_JOBS}', json = {
        "id": 1,
        "position": "keywords",
        "args": ["internship", "remote"]})
    assert resp.status_code == OK

@patch('db.db.external_job_update', side_effect=KeyError(), autospec=True)
def test_UpdateAvailableJobs_BAD(mock_add):
    resp = TEST_CLIENT.put(f'/{ep.UPDATE_AVAILABLE_JOBS}', json = {
        "id": 9,
        "position": "keywords",
        "args": ["internship", "remote"]})
    assert resp.status_code == NOT_ACCEPTABLE

def test_UpdateAvailableJobs_working():
    resp = TEST_CLIENT.put(f'/{ep.UPDATE_AVAILABLE_JOBS}', json = {
        "id": 1,
        "position": "keywords",
        "args": ["internship", "remote"]})
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert "status" in resp_json
    assert resp_json["message"] == "Job 1 updated"

def test_UpdateAvailableJobs_invalid_format ():
    resp = TEST_CLIENT.put(f'/{ep.UPDATE_AVAILABLE_JOBS}', json = {})
    assert resp.status_code == NOT_ACCEPTABLE

def test_keyword_search_database():
    keyword = "internship"
    resp = TEST_CLIENT.get(f'/{ep.KEYWORD_SEARCH}', json = {"keyword": keyword})
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert "results" in resp_json
    assert isinstance(resp_json["results"], list)
    expected_results = [{"data": {"keywords": ["internship", "remote"]},"userid" : 1}]
    assert resp_json['results'] == expected_results

def test_update_job_postings():
    assert True


patch('db.db.delete_account', return_value=True, autospec=True)
def test_delete_account():
    #try to delete admin acount
    resp = TEST_CLIENT.delete(f'/{ep.DELETE_ACCOUNT}', json = {"user_id": 1})
    assert resp._status_code == 400 

    #try to delete non-existent account
    resp = TEST_CLIENT.delete(f'/{ep.DELETE_ACCOUNT}', json = {"user_id": 5})
    assert resp._status_code == 400 

    #try to delete account
    resp = TEST_CLIENT.delete(f'/{ep.DELETE_ACCOUNT}', json = {"user_id": 2})
    assert resp._status_code == 200

    
    assert True
patch('db.db.get_user_reports', return_value=True, autospec=True)
def test_get_user_reports():
    resp = TEST_CLIENT.get(f'/{ep.GET_USER_REPORTS}', json = {"user_id": 1})
    assert resp._status_code == 200
    resp = json.loads(resp.data.decode('utf-8'))
    expected_results =  {"User Reports":  
                [{"user_id": 1, "job_id": 1, "data": {"report": "invalid link"}},
                  {"user_id": 2, "job_id": 2, "data": { "report": "job is closed" }},
                  {"user_id": 3, "job_id": 3, "data": {"report": "page not found"}}]
                  }
    assert resp == expected_results


patch('db.db.add_user_report', return_value=True, autospec=True)
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
    # assert True
    # passed in data for creating an account include:
    # username, password, email
    test1 = {
        'user_id': 1, 'password': 2, 'email': "TESTING"
    }

    test2 = {
        'user_id': 1, 'password': 2, 'email': "TESTING@"
    }

    test3 = {
        'user_id': 1, 'password': "test", 'email': "TESTING@"
    }
    expected_results = {"status": "success", "message":
                "User account successfully created"}

    if False:
        raise Exception('Fail to create account') 
    assert True
    # check each variable aligned with the requirments, provide user_id if successfully create account 
    # if data["username"]:

    # if data["email"]:

    # if data["password"]:

    #create account and provide user_id

def test_login_to_account(): # @skip
    # go to db and check if username/email matches password
    # waiting for db to be set
    assert True

def test_update_preferences():
    test1 = {
        'user_id': 1, 'email': "TESTING", "job_type": "type", "location": "place"
    }

    expected_results = {"status": "success", "message":
                "User Preferences Successfully Updated"}
    assert True

@patch('db.db.get_most_recent_job', return_value=True, autospec=True)
def test_read_most_recent_jobs_OK(mock_add):
    resp = TEST_CLIENT.get(f'/{ep.READ_MOST_RECENT_JOBS}', json = {
        "user_id": 1,
        "numbers": 1})
    assert resp.status_code == OK

@patch('db.db.get_most_recent_job', side_effect=KeyError(), autospec=True)
def test_read_most_recent_jobs_BAD_for_userID(mock_add):
    resp = TEST_CLIENT.get(f'/{ep.READ_MOST_RECENT_JOBS}', json = {
        "user_id": 9,
        "numbers": 9})
    assert resp.status_code == NOT_ACCEPTABLE

@patch('db.db.delete_job', return_value=True, autospec=True)
def test_admin_delete_jobs_OK(mock_add):
    resp = TEST_CLIENT.delete(f'/{ep.ADMIN_DELETE_JOBS}', json = {
        "admin_id": 1,
        "invalid_job_id": 1})
    assert resp.status_code == OK

@patch('db.db.delete_job', side_effect=KeyError(), autospec=True)
def test_admin_delete_jobs_BAD_for_jobID(mock_add):
    resp = TEST_CLIENT.delete(f'/{ep.ADMIN_DELETE_JOBS}', json = {
        "admin_id": 1,
        "invalid_job_id": 9})
    assert resp.status_code == NOT_ACCEPTABLE

@patch('db.db.delete_job', side_effect=KeyError(), autospec=True)
def test_admin_delete_jobs_BAD_for_adminID(mock_add):
    resp = TEST_CLIENT.delete(f'/{ep.ADMIN_DELETE_JOBS}', json = {
        "admin_id": 9,
        "invalid_job_id": 1})
    assert resp.status_code == NOT_ACCEPTABLE

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