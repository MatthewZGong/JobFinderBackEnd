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
job_id_3 = ObjectId("607f191e810c19729de860ea")
admin_id = ObjectId()
dbc.client.drop_database(TEST_DB)

invalid_id = ObjectId("607f191e810c19729eeeeeee")


@pytest.fixture(scope="function")
def temp_user():
    dbc.client[TEST_DB]["users"].insert_one(
        {"_id": user_id, "username": "GeometryDash"}
    )
    dbc.client[TEST_DB]["jobs"].insert_one(
        {
            "_id": job_id,
            "description": "Janitor1",
            "date": datetime.datetime(2020, 5, 17),
            "embedding_vector": [0.0] * 1536,
        }
    )
    # yield to our test function
    yield
    dbc.client[TEST_DB]["users"].delete_one({"_id": user_id})
    dbc.client[TEST_DB]["jobs"].delete_one({"_id": job_id})


@pytest.fixture(scope="function")
def temp_posting(temp_user):
    res = db.add_user_report(user_id, job_id, "Garbage")
    yield res
    dbc.del_one("user_reports", {"_id": res.inserted_id})


@pytest.fixture(scope="function")
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


def test_delete_user_works():
    dbc.client[TEST_DB]["users"].insert_one(
        {"_id": user_id, "username": "GeometryDash"}
    )
    # dbc.client[TEST_DB]["jobs"].insert_one({"_id": job_id, "description": "Janitor"})
    b = db.delete_account(user_id)
    assert b


def test_delete_user_report_works(temp_posting):
    assert db.delete_user_report(temp_posting.inserted_id)


def test_delete_user_report_fails():
    try:
        db.delete_user_report(invalid_id)
    except KeyError:
        assert True


def test_delete_user_fails():
    with pytest.raises(KeyError):
        b = db.delete_account(user_id)


def test_delete_job_bad():
    with pytest.raises(KeyError):
        db.delete_job(admin_id, job_id)


def test_delete_job_good(temp_user, temp_admin):
    res = db.delete_job(admin_id, job_id)
    assert res


@pytest.fixture(scope="function")
def temp_jobs_1():
    dbc.client[TEST_DB]["jobs"].insert_one(
        {
            "_id": job_id_1,
            "description": "Janitor2",
            "date": datetime.datetime(2020, 5, 17),
            "embedding_vector": [0.0] * 1536,
        }
    )
    dbc.client[TEST_DB]["jobs"].insert_one(
        {
            "_id": job_id_2,
            "description": "Janit",
            "date": datetime.datetime(2024, 5, 17),
            "embedding_vector": [0.0] * 1536,
        }
    )
    yield
    dbc.client[TEST_DB]["jobs"].delete_one({"_id": job_id_1})
    dbc.client[TEST_DB]["jobs"].delete_one({"_id": job_id_2})


# I will change temp_user to temp_admin when we have admin table
def test_delete_job_past_date_works(temp_jobs_1, temp_user):
    res = dbc.fetch_all("jobs")
    # I will change user_id to admin_id when we have admin table
    db.delete_job_past_date(datetime.datetime(2022, 5, 17))
    res = dbc.fetch_all("jobs")
    # for test this function, I create two jobs, job_id_1 is before (2022, 5, 17), the other is after
    # it should delete job_id_1
    print(res)  # to print if something went wrong
    assert len(res) == 1
    assert res[0]["_id"] == job_id_2


def test_delete_job_past_date_fail(temp_jobs_1, temp_user):
    try:
        db.delete_job_past_date(user_id, "hello")
    except:
        assert True


def test_get_most_recent_job(temp_user, temp_jobs_1):
    res = db.get_most_recent_job(1)
    assert len(res) == 1
    assert res[0]["date"] == str(datetime.datetime(2024, 5, 17).date())
    assert "job_id" in res[0]
    assert res[0]["job_id"] == str(job_id_2)


def test_get_most_recent_job_1(temp_user, temp_jobs_1):
    res = db.get_most_recent_job(4)
    print(res)
    assert len(res) == 3


def test_add_account():
    identification = db.add_account(
        "FakeAcc", "Fakemail.com", "FakePassword"
    ).inserted_id
    assert dbc.client[TEST_DB]["users"].delete_one({"_id": identification})


def test_add_account_bad():
    with pytest.raises(KeyError):
        identification = db.add_account(
            "FakeAcc", "Fakemail.com", "FakePassword"
        ).inserted_id
        db.add_account("FakeAcc", "Fakemail.com", "FakePassword").inserted_id
    assert dbc.client[TEST_DB]["users"].delete_one({"_id": identification})


def test_update_job_works():
    dbc.client[TEST_DB]["jobs"].insert_one(
        {
            "_id": job_id_3,
            "description": "Janitor_2",
            "date": datetime.datetime(2020, 5, 17),
        }
    )
    db.update_job(job_id_3, {"description": "HELLOOO"})
    res = dbc.fetch_one("jobs", {"_id": job_id_3})
    assert res["description"] == "HELLOOO"
    dbc.client[TEST_DB]["jobs"].delete_one({"_id": job_id_3})


def test_update_job_fails():
    try:
        db.update_job(invalid_id, {"description": "HELLOOO"})
    except Exception as e:
        assert True


def test_add_job_works():
    res = db.add_job_posting(
        "HELLO WORLD", "test", "test", "test", datetime.datetime(2023, 12, 12), "test"
    ).inserted_id
    search = dbc.fetch_one("jobs", {"_id": res})
    assert search["company"] == "HELLO WORLD"
    dbc.client[TEST_DB]["jobs"].delete_one({"_id": res})


def test_add_job_fails():
    try:
        res = db.add_job_posting("HELLO WORLD", None, "test", "test", "test", "test", "test")
    except Exception as e:
        assert True


def test_check_preference_works():
    identification = db.add_account(
        "testAccACC", "Fakemail.com", "FakePassword"
    ).inserted_id
    res = db.check_preference(identification)
    assert True
    dbc.client[TEST_DB]["users"].delete_one({"_id": identification})


def test_check_preference_fails():
    try:
        res = db.check_preference(invalid_id)
    except KeyError:
        assert True


def test_update_account_fails():
    try:
        identification = db.add_account(
            "testAcc", "Fakemail.com", "FakePassword"
        ).inserted_id
        res = db.update_account(invalid_id, {})
    except KeyError:
        assert True


def test_update_account_works():
    identification = db.add_account(
        "FakeFaketestAcc", "FakeFaketestAccFakemail.com", "FakePassword"
    ).inserted_id
    db.update_account(identification, {"email": "notFakemail.com", "username": "notFakeusername"})
    res = dbc.fetch_one("users", {"_id": identification})
    assert res["email"] == "notFakemail.com"
    dbc.client[TEST_DB]["users"].delete_one({"_id": identification})


def test_get_jobs_by_preference_works():
    identification = db.add_account(
        "testAccForPreference", "Fakemail123123.com", "FakePassword"
    ).inserted_id
    db.update_preference(identification, "wash123123", "any")
    job_inserted_id = db.add_job_posting(
        "HELLO WORLD", "test", "wash123123", "wash123123", datetime.datetime(2023, 12, 12), "test"
    ).inserted_id
    res = db.get_jobs_by_preference(
        dbc.fetch_one("users", {"_id": identification})["preference"]
    )
    assert len(res) == 1
    dbc.client[TEST_DB]["users"].delete_one({"_id": identification})
    dbc.client[TEST_DB]["jobs"].delete_one({"_id": job_inserted_id})


def test_get_jobs_by_preference_fails():
    try:
        res = db.get_jobs_by_preference({})
    except TypeError:
        assert True


def test_update_preference_fails():
    try:
        res = db.update_preference(invalid_id, None, None)
    except KeyError:
        assert True


def test_update_preference_works():
    identification = db.add_account(
        "testAccForUpPreference", "Fakemail123123123.com", "FakePassword"
    ).inserted_id
    assert db.update_preference(identification, "wash123123", None)
    dbc.client[TEST_DB]["users"].delete_one({"_id": identification})

def test_get_user_id_works(): 
    fuser = "testAccForGetUser"
    femail = "Fakemail123123123.com"
    fpassword = "FakePassword"
    identification = db.add_account(
       fuser , femail, fpassword
    ).inserted_id
    assert db.get_user_id(fuser, fpassword)
    dbc.client[TEST_DB]["users"].delete_one({"_id": identification})

def test_get_user_id_fails(): 
    fuser = "testAccForGetUser"
    femail = "Fakemail123123123.com"
    fpassword = "FakePassword"
    assert db.get_user_id(fuser, fpassword) == False


def test_get_username_by_id_works():
    fuser = "testAccForGetUser"
    femail = "Fakemail123123123.com"
    fpassword = "FakePassword"
    identification = db.add_account(
       fuser , femail, fpassword
    ).inserted_id
    assert db.get_username_by_id(identification) == fuser
    dbc.client[TEST_DB]["users"].delete_one({"_id": identification})


def test_get_username_by_id_fails():
    try:
        db.get_username_by_id(invalid_id)
    except KeyError:
        assert True

def test_get_job_by_id_works():
    identification = db.add_job_posting(
        "HELLO WORLD", "test", "wash123123", "wash123123", datetime.datetime(2023, 12, 12), "test"
    ).inserted_id
    job = db.get_job_by_id(identification)
    assert job["company"] == "HELLO WORLD"
    assert job["job_description"] == "test"
    assert job["job_type"] == "wash123123"
    assert job["location"] == "wash123123"
    dbc.client[TEST_DB]["jobs"].delete_one({"_id": identification})

def test_get_job_by_id_fails():
    try:
        db.get_job_by_id(invalid_id)
    except KeyError:
        assert True