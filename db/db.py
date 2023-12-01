import db.db_connect as dbc
import datetime
"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
"""

# print(__name__)
dbc.connect_db()

job_data = {
        1: {
            "data": {
                "keywords": ["internship"]
            },
            "userid": 1,
            "date": datetime.datetime(2020, 5, 17)
        },
        2: {
            "data": {
               "keywords": ["Remote"]
            },
            "userid": 2,
            "date": datetime.datetime(2020, 5, 18)
        }
    }

user_data = {
        1: {
            "user_id": 1,
            "data": {
                "username": "new_username",
                "email": "new_email@example.com",
                "password": "new_password"
            }
        }
    }

admin_data = {
        1: {
            "admin_id": 1,
            "data": {
                "username": "new_username",
                "password": "new_password"
            }
        }
    }


user_reports = {
        1: {
            "user_id": 1,
            "job_id": 1,
            "data": {
                "report": "invalid link"
            }
        },
        2: {
            "user_id": 2,
            "job_id": 2,
            "data": {
                "report": "job is closed"
            }
        },
        3: {
            "user_id": 3,
            "job_id": 3,
            "data": {
                "report": "page not found"
            }
        }


    }

user_preference = {
    1: {
        "user_id": 1,
        "preferred location": "string",
        "preferred job type": "string",
        "sort by": ["string"]
    }
}


def add_job_posting(company, job_title, job_description, job_type, location):
    return dbc.insert_one("jobs", {
        "company": company,
        "job_title": job_title,
        "job_description": job_description,
        "job_type": job_type,
        "location": location
    })


def external_job_update(id, position, arg):
    if id in job_data:
        try:
            job_data[id]["data"][position] = arg
            return True
        except Exception as e:
            raise e
    else:
        raise KeyError("id not found")


def delete_job(admin_id, job_id):
    # connect to mongodb to find the jobs corresponding to this
    # job name and delete it, return 1 if suffcessfull deleted, 0 if fail
    if False and not dbc.exists_by_id(admin_id, "admins"):
        raise KeyError(f"No admin {admin_id}")
    if not dbc.exists_by_id(job_id, "jobs"):
        raise KeyError(f"No Job {job_id}")
    return dbc.del_one("jobs", {"_id": job_id})


def delete_job_past_date(admin_id, past_date):
    # connect to mongodb to find the jobs corresponding to date
    # before past_date and delete it
    # change the type of past_date from string to datetime
    if not dbc.exists_by_id(admin_id, "admins"):
        raise KeyError(f"No admin {admin_id}")
    for job in dbc.fetch_all("jobs"):
        if job["date"] < past_date:
            dbc.del_one("jobs", {"_id": job["_id"]})
    return True


def get_most_recent_job(numbers):
    # connect to mongodb to get the numbers of jobs based
    # on their date and store it into job list
    jobs = dbc.fetch_all_as_dict("job_title", "jobs")
    res = {}
    # temporary code for getting recent
    count = 0
    for i in jobs:
        res[i] = jobs[i]
        count += 1
        if count >= numbers:
            break
    return res


def check_account(username, user_password):
    """
    Check whether password/username pair matches an entry in db.
    """
    for i in user_data:
        if username == user_data[i]["data"]["username"]:
            if user_password == user_data[i]["data"]["password"]:
                return True
    return False


def add_account(username, email, password):
    """
    function to add new account
    """
    if check_account(username, password):
        raise KeyError(f"Username already exists {username}")
    else:
        return dbc.insert_one('user_data', {
            "user_id": 10,
            "data": {
                "username": username,
                "email": email,
                "password": password
            }
        })


def update_preference(user_id, preferred_location, preferred_type, sort_by):
    if not dbc.exists_by_id(user_id, "users"):
        raise KeyError(f"No User {user_id}")
    return dbc.insert_one("user_preference",
                          {
                            "user_id": user_id,
                            "preferred location": preferred_location,
                            "preferred job type": preferred_type,
                            "sort by": sort_by
                          })


def delete_account(user_id):
    """
    function to delete an account
    """
    if not dbc.exists_by_id(user_id, "users"):
        raise KeyError(f"No User {user_id}")
    return dbc.del_one("users", {"_id": user_id})


def get_user_reports():
    """
    function to fetch all user reports
    """
    return dbc.fetch_all('user_reports')


def add_user_report(user_id, job_id, report):
    """
    function to add a user report
    """
    if not dbc.exists_by_id(user_id, "users"):
        raise KeyError(f"No User {user_id}")
    if not dbc.exists_by_id(job_id, "jobs"):
        raise KeyError(f"No Job {job_id}")

    return dbc.insert_one('user_reports', {
            "user_id": user_id,
            "job_id": job_id,
            "data": {
                "report": report
            }
        })


def check_preference(user_id):
    """
    function to check and return current user preference
    """
    if not dbc.exists_by_id(user_id, "users"):
        raise KeyError(f"No User {user_id}")
    return True


def delete_user_report(user_id, report_id):
    """
    function to delete a user report
    """
    return True

# if __name__ == "__main__":
#     add_account("test", "test@gmail.com", "test")
