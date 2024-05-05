from bson import ObjectId
from datetime import datetime
import server.endpoints as ep
import json
import pytest

from db import db
from db import db_connect as dbc
from unittest.mock import patch
from http.client import NOT_ACCEPTABLE, OK

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

TEST_DB = dbc.DB_NAME

user_id = ObjectId("507f1f77bcf86cd799439011")
job_id = ObjectId("507f191e810c19729de860ea")
report_id = ObjectId("507f1f77bcf86cd799439012")
job_id_1 = ObjectId()
job_id_2 = ObjectId()
admin_id = ObjectId()

TEST_CLIENT = ep.app.test_client()
dbc.connect_db()

companies = ["Apple", "Microsoft", "Google"]
jobs_type = ["machine learning", "data science", "software engineering"]
fake_vectors = [[float(i+1)] * 1536 for i in range(len(companies))]

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

@pytest.fixture(scope="function")
def temp_user_report(): 
    dbc.client[TEST_DB]["user_reports"].insert_one(
        {"_id": report_id, "user_id": user_id, "job_id": job_id, "data": {"report": "page not found"}}
    )
    yield
    dbc.client[TEST_DB]["user_reports"].delete_one({"_id": report_id})


@pytest.fixture(scope="function")
def temp_jobs():
    ids = []
    for company in companies:
        for i, job_type in enumerate(jobs_type):
            obj = dbc.client[TEST_DB]["jobs"].insert_one(
                {
                    "company": company,
                    "job_description": "",
                    "job_type": job_type,
                    "location": "SF",
                    "date": datetime(2020, 5, 17),
                    "link": f'fakelink/{company}/{job_type}',
                    "embedding_vector": fake_vectors[i],
                }
            )
            ids.append(obj.inserted_id)
    yield

    for id in ids:
        dbc.client[TEST_DB]["jobs"].delete_one({"_id": id})

@pytest.fixture(scope="function")
def vector_search_test(temp_jobs):
    def _mock_vector_search(query_string, limit):
        vector = [0.1]*1536
        for i, job in enumerate(jobs_type):
            if job == query_string: 
                vector = fake_vectors[i]
        res = []
        # print("HI IS THIS WORKING")
        for job in dbc.client[TEST_DB]["jobs"].find({"embedding_vector": vector}):
            # print(job)
            job["id"] = str(job["_id"])
            job["date"] = str(job["date"].date())
            del job["_id"]
            del job["embedding_vector"]
            res.append(job)
        return res
            

    with patch('db.db.search_jobs_by_vector') as mock_vector_search_func:
        mock_vector_search_func.side_effect = lambda x, y: _mock_vector_search(x, y)
        yield mock_vector_search_func




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
            "new_username": "fortnite_player",
            "new_email": "fortnite@epic.com",
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
    print(resp)
    expected_results = [
            {
                "id": "65594839ee7a3c7d7d46eead",
                "data": {"report": "page not found"},
                "job_id": "507f191e810c19729de860ea",
                "user_id": "507f1f77bcf86cd799439011",
            }
        ]
    
    assert resp == expected_results


def test_get_user_reports_empty():
    resp = TEST_CLIENT.get(f"/{ep.GET_USER_REPORTS}")
    assert resp._status_code == 200
    resp = json.loads(resp.data.decode("utf-8"))
    expected_results = []
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


@patch("db.db.check_preference", return_value=True, autospec=True)
def test_get_preferences_BAD(mock_add):
    resp = TEST_CLIENT.get(
        f"/{ep.GET_PREFERENCES}", query_string={"user_id": 5}
    )
    assert resp.status_code == NOT_ACCEPTABLE


@patch("db.db.check_preference", return_value=True, autospec=True)
def test_get_preferences_OK(mock_add):
    resp = TEST_CLIENT.get(
        f"/{ep.GET_PREFERENCES}", query_string={"user_id": '507f191e810c19729de860ea'}
    )
    assert resp.status_code == OK


@patch("db.db.update_preference", return_value=True, autospec=True)
def test_update_preferences_OK(mock_add):
    resp = TEST_CLIENT.put(
        f"/{ep.UPDATE_PREFERENCES}", query_string={"user_id": '507f191e810c19729de860ea', "email": "TESTING", 
                                                      "job_type": "type", "location": "place"}
    )
    assert resp.status_code == OK


@patch("db.db.update_preference", return_value=True, autospec=True)
def test_update_preferences_BAD(mock_add):
    resp = TEST_CLIENT.put(
        f"/{ep.UPDATE_PREFERENCES}", query_string={"user_id": 1, "email": "TESTING", 
                                                      "job_type": "type", "location": "place"}
    )
    assert resp.status_code == NOT_ACCEPTABLE


@patch("db.db.update_preference", return_value=True, autospec=True)
def test_update_preferences_BAD2(mock_add):
    resp = TEST_CLIENT.put(
        f"/{ep.UPDATE_PREFERENCES}", query_string={"user_id": 1, "email": "TESTING"})
    assert resp.status_code == NOT_ACCEPTABLE


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
def test_dev_delete_past_date_OK(mock_add):
    invalid_past_date = datetime(2022, 11, 30)
    # Convert the datetime object to a string with a specific format
    formatted_date = invalid_past_date.strftime("%Y-%m-%d")
    resp = TEST_CLIENT.delete(
        f"/{ep.DEV_DELETE_PAST_DATE}",
        query_string={"invalid_past_date": formatted_date},
    )
    assert resp.status_code == OK


@patch("db.db.delete_job_past_date", side_effect=KeyError(), autospec=True)
def test_dev_delete_past_date_bad(mock_add):
    invalid_past_date = datetime(2022, 11, 30)
    # Convert the datetime object to a string with a specific format
    formatted_date = invalid_past_date.strftime("%Y-%m-%d")
    resp = TEST_CLIENT.delete(
        f"/{ep.DEV_DELETE_PAST_DATE}",
        query_string={"invalid_past_date": formatted_date},
    )
    assert resp.status_code == NOT_ACCEPTABLE


@patch("db.db.add_job_posting", return_value=True, autospec=True)
def test_add_new_job_works(mock_add):
    test = {
        "company": "TESTING",
        "job_description": "TESTING",
        "job_type": "TESTING",
        "location": "TESTING",
        "date": "2022-12-12",
        "link": "https://www.google.com/about/careers/applications/"
    }
    resp = TEST_CLIENT.post(f"/{ep.ADD_NEW_JOBS}", query_string=test)
    assert resp._status_code == 200


@patch("db.db.add_job_posting", return_value=True, autospec=True)
def test_add_new_job_fails(mock_add):
    test = {
        "company": "TESTING",
        "job_description": "TESTING",
        "job_type": "TESTING",
        "location": "TESTING",
        "date": "2022-12-121212",
        "link": "https://www.google.com/about/careers/applications/"
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


@patch("db.db.get_user_id", return_value="FAKE_ID", autospec=True)
def test_login_works(mock_get):
    test = {
        "user_id": "FAKE_USERNAME_123945y43210123",
        "password": "FAKE_PASSWORD_5721394120123123",
    }
    resp = TEST_CLIENT.get(f"/{ep.LOGIN}", query_string=test)
    assert resp._status_code == 200 
    assert resp.get_json()["message"]== "FAKE_ID"

@patch("db.db.get_user_id", return_value=False, autospec=True)
def test_login_fails(mock_get):
    test = {
        "user_id": "FAKE_USERNAME_123945y43210123",
        "password": "FAKE_PASSWORD_5721394120123123",
    }
    resp = TEST_CLIENT.get(f"/{ep.LOGIN}", query_string=test)
    assert resp._status_code == 406


@patch("db.db.get_username_by_id", return_value="FAKE_USERNAME_123945y43210123", autospec=True)
def test_get_username_works(mock_get):
    test = {
        "user_id": "662430e9ab497b02d0c59db0",
    }
    resp = TEST_CLIENT.get(f"/{ep.GET_USERNAME}", query_string=test)
    assert resp._status_code == 200 
    assert resp.get_json()["username"]== "FAKE_USERNAME_123945y43210123"

@patch("db.db.get_username_by_id", return_value=False, autospec=True)
def test_get_username_fails(mock_get):
    test = {
        "user_id": "FAKE_USERNAME_123945y43210123",
    }
    resp = TEST_CLIENT.get(f"/{ep.GET_USERNAME}", query_string=test)
    assert resp._status_code == 400

@patch("db.db.get_job_by_id", return_value={"_id": "507f191e810c19729de860ea",
                                            "company": "Apple", 
                                            "job_description": "Test3", 
                                            "job_type": "Intern", 
                                            "location": "SF",
                                            "date": "2023-12-09"}, autospec=True)
def test_get_job_by_id_works(mock_get):
    test = {
        "job_id": "662430e9ab497b02d0c59db0",
    }
    resp = TEST_CLIENT.get(f"/{ep.GET_JOB_BY_ID}", query_string=test)
    assert resp._status_code == 200 
    assert resp.get_json()["_id"]== "507f191e810c19729de860ea"
    assert resp.get_json()["date"]== "2023-12-09"
    assert resp.get_json()["company"]== "Apple"
    assert resp.get_json()["job_description"]== "Test3"
    assert resp.get_json()["job_type"]== "Intern"
    assert resp.get_json()["location"]== "SF"

@patch("db.db.get_job_by_id", return_value=False, autospec=True)
def test_get_job_by_id_fails(mock_get):
    test = {
        "job_id": "507f191e810c19729de860eamak",
    }
    resp = TEST_CLIENT.get(f"/{ep.GET_JOB_BY_ID}", query_string=test)
    assert resp._status_code == 400


def test_integration_read_most_recent_jobs_works(temp_jobs):
    resp = TEST_CLIENT.get(f"/{ep.READ_MOST_RECENT_JOBS}", query_string={"numbers": len(companies)*len(jobs_type)})
    assert resp._status_code == 200
    assert len(resp.get_json()) == len(companies)*len(jobs_type)
    for job in resp.get_json():
        assert job["company"] in companies
        assert job["job_type"] in jobs_type

def test_integration_read_most_recent_jobs_jobs_num_over_limit(temp_jobs):
    resp = TEST_CLIENT.get(f"/{ep.READ_MOST_RECENT_JOBS}", query_string={"numbers": len(companies)*len(jobs_type)+1})
    assert resp._status_code == 200
    assert len(resp.get_json()) == len(companies)*len(jobs_type)


def test_integration_add_new_jobs(): 
    unique_job_description = "TEST IS A TEST COMING FORM YOU LIVE HAHAHAHAHA12391238473asdfbad9"
    test = {
        "company": companies[0],
        "job_description": unique_job_description,
        "job_type": "Machine Learning",
        "location": "SF",
        "date": "2023-12-09",
        "link": "https://www.google.com/about/careers/applications/"
    }
    resp = TEST_CLIENT.post(f"/{ep.ADD_NEW_JOBS}", query_string=test)
    assert resp._status_code == 200
    job = dbc.fetch_one("jobs", {"job_description": unique_job_description})
    assert job["job_description"] == unique_job_description
    assert job["company"] == companies[0]
    assert job["job_type"] == "Machine Learning"
    assert job["location"] == "SF"
    assert job["link"] == "https://www.google.com/about/careers/applications/"
    dbc.client[TEST_DB]["jobs"].delete_one({"job_description": unique_job_description})

def test_integration_add_new_jobs_fails(): 
    unique_job_description = "TEST IS A TEST COMING FORM YOU LIVE HAHAHAHAHA12391238473asdfbad9"
    test = {
        "company": companies[0],
        "job_description": unique_job_description,
    }
    resp = TEST_CLIENT.post(f"/{ep.ADD_NEW_JOBS}", query_string=test)
    assert resp._status_code == 500

'''
There would be better tests for vector search, but its is only allowed to work on atlas cluster
'''
def test_integration_search_jobs_by_vector_works(temp_jobs, vector_search_test):
    resp = TEST_CLIENT.get(f"/{ep.GET_JOBS_BY_VECTOR}", query_string={"query": "machine learning", "limit": len(companies)*len(jobs_type)})
    assert resp._status_code == 200
    assert len(resp.get_json()) == len(companies)
    for job in resp.get_json():
        assert job["job_type"] == "machine learning"

def test_integration_search_jobs_by_vector_with_no_results(temp_jobs, vector_search_test):
    resp = TEST_CLIENT.get(f"/{ep.GET_JOBS_BY_VECTOR}", query_string={"query": "not machine learning", "limit": 3})
    assert resp._status_code == 200
    assert len(resp.get_json()) == 0

def test_integration_search_jobs_by_vector_with_bad_limit(temp_jobs, vector_search_test):
    resp = TEST_CLIENT.get(f"/{ep.GET_JOBS_BY_VECTOR}", query_string={"query": "machine learning", "limit": 0})
    assert resp._status_code == 400 

    # eprint(resp.get_json()

def test_integration_get_jobs_by_id_works(temp_jobs):
    for jobs in dbc.fetch_all("jobs"):
        resp = TEST_CLIENT.get(f"/{ep.GET_JOB_BY_ID}", query_string={"job_id": jobs["_id"]})
        # print(resp.get_json())
        assert resp._status_code == 200
        assert ObjectId(resp.get_json()["_id"]) == jobs["_id"]
        assert resp.get_json()["company"] == jobs["company"]
        assert resp.get_json()["job_description"] == jobs["job_description"]
        assert resp.get_json()["job_type"] == jobs["job_type"]
        assert resp.get_json()["location"] == jobs["location"]

def test_integration_get_user(temp_user):
    resp = TEST_CLIENT.get(f"/{ep.GET_USERNAME}", query_string={"user_id": user_id})
    print(resp.get_json())
    assert resp._status_code == 200
    assert resp.get_json()["username"] =="GeometryDash"

def test_integration_delete_user_report_works(temp_user_report):
    assert dbc.fetch_one("user_reports", {"_id": report_id}) is not None
    resp = TEST_CLIENT.delete(f"/{ep.DELETE_USER_REPORT}", query_string={"report_id": report_id})
    assert dbc.fetch_one("user_reports", {"_id": report_id}) is None
    assert resp._status_code == 200

def test_integration_delete_user_report_fails(temp_user_report):
    resp = TEST_CLIENT.delete(f"/{ep.DELETE_USER_REPORT}", query_string={"report_id": 12345})
    assert resp._status_code == 406