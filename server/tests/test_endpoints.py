from bson import ObjectId
from datetime import datetime
import server.endpoints as ep
import json
import pytest

from db import db
from db import db_connect as dbc
from unittest.mock import patch
from http.client import (
    NOT_ACCEPTABLE,
    OK
)

TEST_CLIENT = ep.app.test_client()
dbc.connect_db()


@pytest.fixture
def sample_data():
    return {
        "user_id": 1123,
        "data": {
            "username": "new_username",
            "email": "new_email@example.com"
        }
    }

def sample_get_users():
    return [{'_id': '65594839ee7a3c7d7d46eead',
    'data': {'report': 'page not found'},
    'job_id': '507f191e810c19729de860ea',
    'user_id': '507f1f77bcf86cd799439011'}]

def test_update_user_info():

    resp = TEST_CLIENT.put(f'/{ep.UPDATE_USER_INFO}', json={"_id": 1})
    resp_json = resp.get_json()
    
    assert isinstance(resp_json, dict)
    assert 'status' in resp_json
    assert resp_json['status'] == 'success'
    assert 'message' in resp_json
    assert resp_json['message'] == f"User {1} info updated"


def test_update_user_info_bad(sample_data):
    test = sample_data

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
    expected_results = [{"data": {"keywords": ["internship", "remote"]},"userid" : 1, "date": datetime(2020, 5, 17).isoformat()}]
    assert resp_json['results'] == expected_results

def test_update_job_postings():
    assert True

def test_delete_account():
    resp = TEST_CLIENT.delete(f'/{ep.DELETE_ACCOUNT}', json = {"user_id": "507f191e810c19729de860ea"})

    assert resp._status_code == NOT_ACCEPTABLE 
    assert {'message': "'No User 507f191e810c19729de860ea'"} == resp.get_json()

@patch('db.db.delete_account', return_value=True, autospec=True)
def test_delete_account_mockgood(mock):
    resp = TEST_CLIENT.delete(f'/{ep.DELETE_ACCOUNT}', json = {"user_id": "507f191e810c19729de860ea"})

    assert resp._status_code == 200 
    assert {"message": f"Successfully deleted 507f191e810c19729de860ea"} == resp.get_json()

def test_delete_account_real():
    identification = db.add_account('new_user', 'new_email').inserted_id
    resp = TEST_CLIENT.delete(f'/{ep.DELETE_ACCOUNT}', json = {"user_id": str(identification)})
    assert resp._status_code == 200 
    assert {"message": f"Successfully deleted {str(identification)}"} == resp.get_json()

@patch('db.db.get_user_reports', 
    return_value=sample_get_users(), autospec=True)
def test_get_user_reports(mock_get):
    resp = TEST_CLIENT.get(f'/{ep.GET_USER_REPORTS}', json = {"user_id": 1})
    assert resp._status_code == 200
    resp = json.loads(resp.data.decode('utf-8'))
    expected_results =  {"User Reports": [{'_id': '65594839ee7a3c7d7d46eead',
    'data': {'report': 'page not found'},
    'job_id': '507f191e810c19729de860ea',
    'user_id': '507f1f77bcf86cd799439011'}]}
    assert resp == expected_results


patch('db.db.add_user_report', return_value=[True], autospec=True)
def test_send_user_report():
    resp = TEST_CLIENT.post(f'/{ep.USER_REPORT}', json={
        'user_id': 1, 'job_id': 1, "report": "TESTING"
    })
    assert resp._status_code == 200
    resp = json.loads(resp.data.decode('utf-8'))
    expected_results = {"status": "success", "message":
                "User report successfully submitted report"}
                
    assert resp == expected_results  


    resp = TEST_CLIENT.post(f'/{ep.USER_REPORT}', json={
        'user_id': 10, 'job_id': 1, "report": "TESTING"
    })
    assert resp._status_code == 400
    resp = json.loads(resp.data.decode('utf-8'))
    expected_results =  {"status": "failure", "message":
                "Invalid User ID"}
    assert resp == expected_results 

    resp = TEST_CLIENT.post(f'/{ep.USER_REPORT}', json={
        'user_id': 1, 'job_id': 1, "report": ""
    })
    assert resp._status_code == 400
    resp = json.loads(resp.data.decode('utf-8'))
    expected_results =  {"status": "failure", "message":
                "Invalid report"}
    assert resp == expected_results

@patch('db.db.add_account', return_value=True, autospec=True)
def test_create_account_success(mock):
    # Test data with new username and email
    test_data = {
        'username': 'new_user',
        'email': 'new_email@example.com'
    }
    expected = {"status": "success", "message": "Account new_user successfully created"}

    resp = TEST_CLIENT.put(f'/{ep.CREATE_USER_ACCOUNT}', json=test_data)
    text = json.loads(resp.data.decode('utf-8'))
    assert resp._status_code == 200
    assert text == expected

@patch('db.db.add_account', side_effect=KeyError("User with Username or email already exists"), autospec=True)
def test_create_account_bad(mock):
    # Test data with new username and email
    test_data = {
        'username': 'new_user',
        'email': 'new_email@example.com'
    }
    expected = {'message': "'User with Username or email already exists'"}

    resp = TEST_CLIENT.put(f'/{ep.CREATE_USER_ACCOUNT}', json=test_data)
    text = json.loads(resp.data.decode('utf-8'))
    assert resp._status_code == NOT_ACCEPTABLE
    assert text == expected

@pytest.mark.skip('Useless Test')
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
    resp = TEST_CLIENT.get(f'/{ep.READ_MOST_RECENT_JOBS}', query_string = {
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
    resp = TEST_CLIENT.delete(f'/{ep.ADMIN_DELETE_JOBS}', query_string = {
        "admin_id": 1,
        "job_id": '507f1f77bcf86cd799439011'})
    assert resp.status_code == OK

@patch('db.db.delete_job', side_effect=KeyError(), autospec=True)
def test_admin_delete_jobs_BAD_for_jobID(mock_add):
    resp = TEST_CLIENT.delete(f'/{ep.ADMIN_DELETE_JOBS}', json = {
        "admin_id": 1,
        "job_id": 9})
    assert resp.status_code == NOT_ACCEPTABLE

@patch('db.db.delete_job', side_effect=KeyError(), autospec=True)
def test_admin_delete_jobs_BAD_for_adminID(mock_add):
    resp = TEST_CLIENT.delete(f'/{ep.ADMIN_DELETE_JOBS}', json = {
        "admin_id": 9,
        "invalid_job_id": 1})
    assert resp.status_code == NOT_ACCEPTABLE

@patch('db.db.delete_job_past_date', return_value=True, autospec=True)
def test_admin_delete_past_date_OK(mock_add):
    invalid_past_date = datetime(2022, 11, 30)
    # Convert the datetime object to a string with a specific format
    formatted_date = invalid_past_date.strftime('%Y-%m-%d')
    resp = TEST_CLIENT.delete(f'/{ep.ADMIN_DELETE_PAST_DATE}', json = {
        "admin_id": 1,
        "invalid_past_date": formatted_date})
    assert resp.status_code == OK

@patch('db.db.delete_job_past_date', side_effect=KeyError(), autospec=True)
def test_admin_delete_past_date_bad(mock_add):
    invalid_past_date = datetime(2022, 11, 30)
    # Convert the datetime object to a string with a specific format
    formatted_date = invalid_past_date.strftime('%Y-%m-%d')
    resp = TEST_CLIENT.delete(f'/{ep.ADMIN_DELETE_PAST_DATE}', json = {
        "admin_id": 9,
        "invalid_past_date": formatted_date})
    assert resp.status_code ==  NOT_ACCEPTABLE
