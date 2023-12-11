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


def add_job_posting(company, job_title,
                    job_description, job_type, location, date):
    return dbc.insert_one("jobs", {
        "company": company,
        "job_title": job_title,
        "job_description": job_description,
        "job_type": job_type,
        "location": location,
        'date': date
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


def update_job(job_id, changes):
    """
    function to update the parameters of a job
    """
    if not dbc.exists_by_id(job_id, "jobs"):
        raise KeyError(f"No User {job_id}")
    return dbc.update_doc("jobs", {"_id": job_id}, changes)


def delete_job(admin_id, job_id):
    # connect to mongodb to find the jobs corresponding to this
    # job name and delete it, return 1 if suffcessfull deleted, 0 if fail
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
    # jobs is a dictionary, key is date
    jobs = dbc.fetch_all_as_dict("date", "jobs")
    sorted_key = sorted(jobs)
    # find the most recent numbers of jobs based on key
    last_keys = sorted_key[-numbers:]
    res = [jobs[key] for key in last_keys]
    for entry in res:
        entry['date'] = str(entry['date'].date())
    return res


def check_account(user_id, username, password):
    """
    Check whether password/username pair matches an entry in db.
    """
    if not dbc.exists_by_id(user_id, "users"):
        raise KeyError(f"No User {user_id}")
    else:
        user = dbc.find_by_id(user_id, "users")
        if user["username"] == username and user["password"] == password:
            return True
        raise KeyError("Invalid password or username")


def add_account(username, email, password):
    """
    function to add new account
    """
    exist = dbc.fetch_one("users", {"username": username})
    exist = exist or dbc.fetch_one("users", {"email": email})
    if exist:
        raise KeyError("User with Username or email already exists")
    else:
        return dbc.insert_one('users', {
            "username": username,
            "email": email,
            "password": password,
            "preference": {
                            "preferred location": None,
                            "preferred job type": None,
                            "sort by": None
            }
        })


def get_jobs_by_preference(preference):
    """
    function to get jobs based on user preference
    """
    all = dbc.fetch_all("jobs")
    return_list = []
    for job in all:
        if job["location"] == preference["location"]:
            return_list += [job]
        if job not in return_list:
            if job["job_type"] == preference["job_type"]:
                return_list += [job]
    return return_list


def update_preference(user_id, preferred_location, preferred_type, sort_by):
    if not dbc.exists_by_id(user_id, "users"):
        raise KeyError(f"No User {user_id}")
    return dbc.update_doc("users", {"_id": user_id},
                          {
        "preferred location": preferred_location,
        "preferred job type": preferred_type,
        "sort by": sort_by
    })


def update_account(user_id, changes):
    """
    function to update the parameters of a user
    """
    if not dbc.exists_by_id(user_id, "users"):
        raise KeyError(f"No User {user_id}")
    return dbc.update_doc("users", {"_id": user_id}, changes)


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
    else:
        user = dbc.find_by_id(user_id, "users")
        return user["preference"]


def delete_user_report(report_id):
    """
    function to delete a user report
    """
    if not dbc.exists_by_id(report_id, "user_reports"):
        raise KeyError(f"No Report_ID {report_id}")
    return dbc.del_one("user_reports", {"_id": report_id})

# if __name__ == "__main__":
#     add_account("test", "test@gmail.com", "test")
