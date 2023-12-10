from bson import ObjectId
import db.db as db
import pytest
import db.db_connect as dbc
import datetime
TEST_DB = dbc.DB_NAME

user_id = ObjectId("507f1f77bcf86cd799439011")
job_id = ObjectId("507f191e810c19729de860ea")
job_id_1 = ObjectId()
job_id_2 = ObjectId()
admin_id = ObjectId()
dbc.client.drop_database(TEST_DB)


@pytest.fixture(scope='function')
def temp_user():
    dbc.client[TEST_DB]["users"].insert_one({"_id": user_id, "username": "GeometryDash"})
    dbc.client[TEST_DB]["jobs"].insert_one({"_id": job_id, "description": "Janitor",
                                            "date": datetime.datetime(2020, 5, 17)})
    # yield to our test function
    yield
    dbc.client[TEST_DB]["users"].delete_one({"_id": user_id})
    dbc.client[TEST_DB]["jobs"].delete_one({"_id": job_id})

@pytest.fixture(scope='function')
def temp_posting(temp_user):
    res = db.add_user_report(user_id, job_id, "Garbage")
    yield res
    dbc.del_one("user_reports", {"_id": res.inserted_id})

@pytest.fixture(scope='function')
def temp_admin():
    dbc.client[TEST_DB]["admins"].insert_one({"_id": admin_id, "username": "Captain"})
    yield
    dbc.client[TEST_DB]["admins"].delete_one({"_id": admin_id})

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

def test_delete_user():
    dbc.client[TEST_DB]["users"].insert_one({"_id": user_id, "username": "GeometryDash"})
    # dbc.client[TEST_DB]["jobs"].insert_one({"_id": job_id, "description": "Janitor"})
    b = db.delete_account(user_id)
    assert b

def test_delete_user_report(temp_posting):
    assert db.delete_user_report(temp_posting.inserted_id)

def test_delete_user():
    with pytest.raises(KeyError):
        b = db.delete_account(user_id)

def test_delete_job_bad():
    with pytest.raises(KeyError):
        db.delete_job(admin_id, job_id)

def test_delete_job_good(temp_user, temp_admin):
    res = db.delete_job(admin_id, job_id)
    assert res

@pytest.fixture(scope='function')
def temp_jobs_1():
    dbc.client[TEST_DB]["jobs"].insert_one({"_id": job_id_1, "description": "Janitor", "date": datetime.datetime(2020, 5, 17)})
    dbc.client[TEST_DB]["jobs"].insert_one({"_id": job_id_2, "description": "Janit", "date": datetime.datetime(2024, 5, 17)})
    yield
    dbc.client[TEST_DB]["jobs"].delete_one({"_id": job_id_1})
    dbc.client[TEST_DB]["jobs"].delete_one({"_id": job_id_2})

def test_delete_job_past_date(temp_jobs_1, temp_admin):
    res = dbc.fetch_all("jobs")
    db.delete_job_past_date(admin_id, datetime.datetime(2022, 5, 17))
    res = dbc.fetch_all("jobs")
    # for test this function, I create two jobs, job_id_1 is before (2022, 5, 17), the other is after
    # it should delete job_id_1
    print(res) # to print if something went wrong
    assert len(res) == 1
    assert res[0]["_id"] == job_id_2

def test_get_most_recent_job(temp_user, temp_jobs_1):
    res=db.get_most_recent_job(1)
    assert len(res)==1
    assert res[0]["date"] == datetime.datetime(2024, 5, 17)

def test_get_most_recent_job_1(temp_user, temp_jobs_1):
    res=db.get_most_recent_job(3)
    assert len(res)==2
    assert res[0]["date"] == datetime.datetime(2020, 5, 17)
    assert res[1]["date"] == datetime.datetime(2024, 5, 17)

def test_add_account():
    identification = db.add_account("FakeAcc", "Fakemail.com", "FakePassword").inserted_id
    assert dbc.client[TEST_DB]["users"].delete_one({"_id": identification})

def test_add_account_bad():
    with pytest.raises(KeyError):
        identification = db.add_account("FakeAcc", "Fakemail.com", "FakePassword").inserted_id
        db.add_account("FakeAcc", "Fakemail.com", "FakePassword").inserted_id
    assert dbc.client[TEST_DB]["users"].delete_one({"_id": identification})
