from bson import ObjectId
from datetime import datetime
import server.endpoints as ep
import json
import pytest

from db import db
from db import db_connect as dbc
from unittest.mock import patch
from http.client import NOT_ACCEPTABLE, OK

TEST_DB = dbc.DB_NAME

user_id = ObjectId("507f1f77bcf86cd799439011")
job_id = ObjectId("507f191e810c19729de860ea")
job_id_1 = ObjectId()
job_id_2 = ObjectId()
admin_id = ObjectId()

TEST_CLIENT = ep.app.test_client()
dbc.connect_db()


@pytest.fixture
def sample_data():
    return {
        "user_id": 1123,
        "data": {"username": "new_username", "email": "new_email@example.com"},
    }


def sample_get_users():
    return [
        {
            "_id": "65594839ee7a3c7d7d46eead",
            "data": {"report": "page not found"},
            "job_id": "507f191e810c19729de860ea",
            "user_id": "507f1f77bcf86cd799439011",
        }
    ]


@pytest.fixture(scope="function")
def temp_user():
    dbc.client[TEST_DB]["users"].insert_one(
        {"_id": user_id, "username": "GeometryDash"}
    )
    # yield to our test function
    yield
    dbc.client[TEST_DB]["users"].delete_one({"_id": user_id})


def test_update_user_info_bad():
    resp = TEST_CLIENT.put(
        f"/{ep.UPDATE_USER_INFO}",
        query_string={"_id": "65594839ee7a3c7d7d46eead", "changes": {}},
    )
    resp_json = resp.get_json()

    assert resp._status_code == NOT_ACCEPTABLE
    assert resp_json == {"message": "'No User 65594839ee7a3c7d7d46eead'"}


def test_update_user_info(temp_user):
    resp = TEST_CLIENT.put(
        f"/{ep.UPDATE_USER_INFO}",
        query_string={
            "_id": "507f1f77bcf86cd799439011",
            "username": "fortnite_player",
            "email": "fortnite@epic.com",
        },
    )
    resp_json = resp.get_json()

    assert resp._status_code == 200
    assert resp_json == {
        "status": "success",
        "message": "User 507f1f77bcf86cd799439011 info updated",
    }


def test_update_user_info_bad(sample_data):
    test = sample_data

    resp = TEST_CLIENT.put(f"/{ep.UPDATE_USER_INFO}", query_string=test)
    assert resp.status_code == NOT_ACCEPTABLE


# def test_keyword_search_database():
#     keyword = "internship"
#     resp = TEST_CLIENT.get(f'/{ep.KEYWORD_SEARCH}', json = {"keyword": keyword})
#     resp_json = resp.get_json()
#     assert isinstance(resp_json, dict)
#     assert "results" in resp_json
#     assert isinstance(resp_json["results"], list)
#     expected_results = [{"data": {"keywords": ["internship", "remote"]},"userid" : 1, "date": datetime(2020, 5, 17)}]
#     assert resp_json['results'] == expected_results
@patch("db.db.update_job", return_value=True)
def test_update_job_postings_works(mock):
    resp = TEST_CLIENT.put(
        f"/{ep.UPDATE_JOB_POSTING}", query_string={"job_id": "507f1f77bcf86cd799439011"}
    )
    print("got past")
    resp_json = resp.get_json()
    print(resp_json)
    assert resp._status_code == 200
    assert resp_json == {"status": "success", "message": "Job posting updated"}


@patch("db.db.update_job", return_value=True)
def test_update_job_postings_should_fail_job_id(mock):
    resp = TEST_CLIENT.put(
        f"/{ep.UPDATE_JOB_POSTING}", query_string={"job_id": "507f1f77b"}
    )
    print("got past")
    resp_json = resp.get_json()
    print(resp_json)
    assert resp._status_code == 406
    assert resp_json == {
        "message": "'507f1f77b' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string"
    }


@patch("db.db.update_job", return_value=True)
def test_update_job_postings_should_fail_date(mock):
    resp = TEST_CLIENT.put(
        f"/{ep.UPDATE_JOB_POSTING}",
        query_string={"job_id": "507f1f77bcf86cd799439011", "date": "123-123-123"},
    )
    print("got past")
    resp_json = resp.get_json()
    print(resp_json)
    assert resp._status_code == 406
    assert resp_json == {
        "message": "time data '123-123-123' does not match format '%Y-%m-%d'",
    }


def test_delete_account():
    resp = TEST_CLIENT.delete(
        f"/{ep.DELETE_ACCOUNT}", query_string={"user_id": "507f191e810c19729de860ea"}
    )

    assert resp._status_code == NOT_ACCEPTABLE
    assert {"message": "'No User 507f191e810c19729de860ea'"} == resp.get_json()


@patch("db.db.delete_account", return_value=True, autospec=True)
def test_delete_account_mockgood(mock):
    resp = TEST_CLIENT.delete(
        f"/{ep.DELETE_ACCOUNT}", query_string={"user_id": "507f191e810c19729de860ea"}
    )

    assert resp._status_code == 200
    assert {
        "message": f"Successfully deleted 507f191e810c19729de860ea"
    } == resp.get_json()


def test_delete_account_real():
    identification = db.add_account("new_user", "new_email", "new_password").inserted_id
    resp = TEST_CLIENT.delete(
        f"/{ep.DELETE_ACCOUNT}", query_string={"user_id": str(identification)}
    )
    assert resp._status_code == 200
    assert {"message": f"Successfully deleted {str(identification)}"} == resp.get_json()


@patch("db.db.get_user_reports", return_value=sample_get_users(), autospec=True)
def test_get_user_reports_mock(mock_get):
    resp = TEST_CLIENT.get(f"/{ep.GET_USER_REPORTS}")
    assert resp._status_code == 200
    resp = json.loads(resp.data.decode("utf-8"))
    expected_results = {
        "User Reports": [
            {
                "_id": "65594839ee7a3c7d7d46eead",
                "data": {"report": "page not found"},
                "job_id": "507f191e810c19729de860ea",
                "user_id": "507f1f77bcf86cd799439011",
            }
        ]
    }
    assert resp == expected_results


def test_get_user_reports_empty():
    resp = TEST_CLIENT.get(f"/{ep.GET_USER_REPORTS}")
    assert resp._status_code == 200
    resp = json.loads(resp.data.decode("utf-8"))
    expected_results = {"User Reports": []}
    assert resp == expected_results


@patch("db.db.add_user_report", return_value=True, autospec=True)
def test_send_user_report(mock_add):
    resp = TEST_CLIENT.post(
        f"/{ep.USER_REPORT}",
        query_string={"user_id": 1, "job_id": 1, "report": "TESTING"},
    )
    assert resp._status_code == OK


@patch("db.db.add_user_report", side_effect=KeyError(), autospec=True)
def test_send_user_report_bad(mock_add):
    resp = TEST_CLIENT.post(
        f"/{ep.USER_REPORT}",
        query_string={"user_id": 10, "job_id": 1, "report": "TESTING"},
    )
    assert resp._status_code == NOT_ACCEPTABLE


@patch("db.db.add_account", return_value=True, autospec=True)
def test_create_account_success(mock):
    # Test data with new username and email
    test_data = {
        "username": "new_user",
        "email": "new_email@example.com",
        "password": "new_password",
    }
    expected = {"status": "success", "message": "Account new_user successfully created"}

    resp = TEST_CLIENT.put(f"/{ep.CREATE_USER_ACCOUNT}", query_string=test_data)
    text = json.loads(resp.data.decode("utf-8"))
    assert resp._status_code == 200
    assert text == expected


@patch(
    "db.db.add_account",
    side_effect=KeyError("User with Username or email already exists"),
    autospec=True,
)
def test_create_account_bad(mock):
    # Test data with new username and email
    test_data = {
        "username": "new_user",
        "email": "new_email@example.com",
        "password": "new_password",
    }
    expected = {"message": "'User with Username or email already exists'"}

    resp = TEST_CLIENT.put(f"/{ep.CREATE_USER_ACCOUNT}", query_string=test_data)
    text = json.loads(resp.data.decode("utf-8"))
    assert resp._status_code == NOT_ACCEPTABLE
    assert text == expected


@pytest.mark.skip("Useless Test")
def test_login_to_account():  # @skip
    # go to db and check if username/email matches password
    # waiting for db to be set
    assert True


def test_update_preferences():
    test1 = {"user_id": 1, "email": "TESTING", "job_type": "type", "location": "place"}

    expected_results = {
        "status": "success",
        "message": "User Preferences Successfully Updated",
    }
    assert True


@patch("db.db.update_preference", return_value=True, autospec=True)
def test_update_preferences_OK(mock_add):
    resp = TEST_CLIENT.get(
        f"/{ep.READ_MOST_RECENT_JOBS}", query_string={"user_id": 1, "email": "TESTING", 
                                                      "job_type": "type", "location": "place"}
    )
    assert resp.status_code == OK


@patch("db.db.get_most_recent_job", return_value=True, autospec=True)
def test_read_most_recent_jobs_OK(mock_add):
    resp = TEST_CLIENT.get(
        f"/{ep.READ_MOST_RECENT_JOBS}", query_string={"user_id": 1, "numbers": 1}
    )
    assert resp.status_code == OK


@patch("db.db.get_most_recent_job", side_effect=KeyError(), autospec=True)
def test_read_most_recent_jobs_BAD_for_userID(mock_add):
    resp = TEST_CLIENT.get(
        f"/{ep.READ_MOST_RECENT_JOBS}", json={"user_id": 9, "numbers": 9}
    )
    assert resp.status_code == NOT_ACCEPTABLE


@patch("db.db.delete_job", return_value=True, autospec=True)
def test_admin_delete_jobs_OK(mock_add):
    resp = TEST_CLIENT.delete(
        f"/{ep.ADMIN_DELETE_JOBS}",
        query_string={"admin_id": 1, "job_id": "507f1f77bcf86cd799439011"},
    )
    assert resp.status_code == OK


@patch("db.db.delete_job", side_effect=KeyError(), autospec=True)
def test_admin_delete_jobs_BAD_for_jobID(mock_add):
    resp = TEST_CLIENT.delete(
        f"/{ep.ADMIN_DELETE_JOBS}", json={"admin_id": 1, "job_id": 9}
    )
    assert resp.status_code == NOT_ACCEPTABLE


@patch("db.db.delete_job", side_effect=KeyError(), autospec=True)
def test_admin_delete_jobs_BAD_for_adminID(mock_add):
    resp = TEST_CLIENT.delete(
        f"/{ep.ADMIN_DELETE_JOBS}", json={"admin_id": 9, "invalid_job_id": 1}
    )
    assert resp.status_code == NOT_ACCEPTABLE


@patch("db.db.delete_job_past_date", return_value=True, autospec=True)
def test_admin_delete_past_date_OK(mock_add):
    invalid_past_date = datetime(2022, 11, 30)
    # Convert the datetime object to a string with a specific format
    formatted_date = invalid_past_date.strftime("%Y-%m-%d")
    resp = TEST_CLIENT.delete(
        f"/{ep.ADMIN_DELETE_PAST_DATE}",
        query_string={"admin_id": 1, "invalid_past_date": formatted_date},
    )
    assert resp.status_code == OK


@patch("db.db.delete_job_past_date", side_effect=KeyError(), autospec=True)
def test_admin_delete_past_date_bad(mock_add):
    invalid_past_date = datetime(2022, 11, 30)
    # Convert the datetime object to a string with a specific format
    formatted_date = invalid_past_date.strftime("%Y-%m-%d")
    resp = TEST_CLIENT.delete(
        f"/{ep.ADMIN_DELETE_PAST_DATE}",
        query_string={"admin_id": 9, "invalid_past_date": formatted_date},
    )
    assert resp.status_code == NOT_ACCEPTABLE


@patch("db.db.add_job_posting", return_value=True, autospec=True)
def test_add_new_job_works(mock_add):
    test = {
        "company": "TESTING",
        "job_title": "TESTING",
        "job_description": "TESTING",
        "job_type": "TESTING",
        "location": "TESTING",
        "date": "2022-12-12",
    }
    resp = TEST_CLIENT.post(f"/{ep.ADD_NEW_JOBS}", query_string=test)
    assert resp._status_code == 200


@patch("db.db.add_job_posting", return_value=True, autospec=True)
def test_add_new_job_fails(mock_add):
    test = {
        "company": "TESTING",
        "job_title": "TESTING",
        "job_description": "TESTING",
        "job_type": "TESTING",
        "location": "TESTING",
        "date": "2022-12-121212",
    }
    resp = TEST_CLIENT.post(f"/{ep.ADD_NEW_JOBS}", query_string=test)
    assert resp._status_code == 406


@patch("db.db.delete_user_report", return_value=True, autospec=True)
def test_delete_user_report_works(mock_add):
    test = {
        "report_id": "507f1f77bcf86cd799439011",
    }
    resp = TEST_CLIENT.delete(f"/{ep.DELETE_USER_REPORT}", query_string=test)
    assert resp._status_code == 200


@patch("db.db.delete_user_report", return_value=True, autospec=True)
def test_delete_user_report_fails(mock_add):
    test = {
        "report_id": "507f1f77bcf86cd7994390",
    }
    resp = TEST_CLIENT.delete(f"/{ep.DELETE_USER_REPORT}", query_string=test)
    assert resp._status_code == 406


@patch("db.db.get_jobs_by_preference", return_value=True, autospec=True)
@patch("db.db.check_preference", return_value=True, autospec=True)
def test_get_jobs_based_on_preference_works(mock_get, mock_check):
    test = {
        "user_id": "507f1f77bcf86cd799439011",
    }
    resp = TEST_CLIENT.get(f"/{ep.GET_JOBS_BASED_ON_PREFERENCE}", query_string=test)
    assert resp._status_code == 200


@patch("db.db.get_jobs_by_preference", return_value=True, autospec=True)
@patch("db.db.check_preference", return_value=True, autospec=True)
def test_get_jobs_based_on_preference_fails(mock_get, mock_check):
    test = {
        "user_id": "507f1f77bcf86cd79943901",
    }
    resp = TEST_CLIENT.get(f"/{ep.GET_JOBS_BASED_ON_PREFERENCE}", query_string=test)
    assert resp._status_code == 406
