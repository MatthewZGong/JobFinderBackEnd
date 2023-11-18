import db.db as db
import pytest
import db.db_connect as dbc

TEST_DB = dbc.DB_NAME

@pytest.fixture(scope='function')
def temp_user():
    user_id = "507f1f77bcf86cd799439011"
    job_id = "507f191e810c19729de860ea"
    dbc.client[TEST_DB]["users"].insert_one({"_id": user_id, "username": "GeometryDash"})
    dbc.client[TEST_DB]["jobs"].insert_one({"_id": job_id, "description": "Janitor"})
    # yield to our test function
    yield
    dbc.client[TEST_DB]["users"].delete_one({"_id": user_id})
    dbc.client[TEST_DB]["jobs"].delete_one({"_id": job_id})

def test_add_user_report_bad():
    user_id = "507f1f77bcf86cd799439011"
    job_id = "507f191e810c19729de860ea"

    with pytest.raises(KeyError):
        db.add_user_report(user_id, job_id, "Garbage")

def test_add_user_report_good(temp_user):
    user_id = "507f1f77bcf86cd799439011"
    job_id = "507f191e810c19729de860ea"

    assert db.add_user_report(user_id, job_id, "Garbage")