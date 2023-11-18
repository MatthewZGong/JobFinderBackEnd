import db.db as db
import pytest

def test_hello():
    assert True

def test_add_user_report_bad():
    user_id = "507f1f77bcf86cd799439011"
    job_id = "507f191e810c19729de860ea"

    with pytest.raises(KeyError):
        db.add_user_report(user_id, job_id, "Garbage")