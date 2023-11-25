from bson import ObjectId
import db.db as db
import pytest
import db.db_connect as dbc

TEST_DB = dbc.DB_NAME

user_id = ObjectId("507f1f77bcf86cd799439011")
job_id = ObjectId("507f191e810c19729de860ea")
dbc.client.drop_database(TEST_DB)

@pytest.fixture(scope='function')
def temp_user():
    dbc.client[TEST_DB]["users"].insert_one({"_id": user_id, "username": "GeometryDash"})
    dbc.client[TEST_DB]["jobs"].insert_one({"_id": job_id, "description": "Janitor"})
    # yield to our test function
    yield
    dbc.client[TEST_DB]["users"].delete_one({"_id": user_id})
    dbc.client[TEST_DB]["jobs"].delete_one({"_id": job_id})

@pytest.fixture(scope='function')
def temp_posting(temp_user):
    res = db.add_user_report(user_id, job_id, "Garbage")
    yield
    dbc.del_one("user_reports", {"_id": res.inserted_id})

def test_add_user_report_bad():
    with pytest.raises(KeyError):
        db.add_user_report(user_id, job_id, "Garbage")

def test_add_user_report_good(temp_user):
    res = db.add_user_report(user_id, job_id, "Garbage")
    assert res
    dbc.del_one("user_reports", {"_id": res.inserted_id})

def test_get_user_report(temp_user, temp_posting):
    b = db.get_user_reports()
    assert len(b) == 1
