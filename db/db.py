import db.db_connect as dbc
import datetime
from copy import deepcopy

"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
"""

# print(__name__)
dbc.connect_db()

job_data = {
    1: {
        "data": {"keywords": ["internship"]},
        "userid": 1,
        "date": datetime.datetime(2020, 5, 17),
    },
    2: {
        "data": {"keywords": ["Remote"]},
        "userid": 2,
        "date": datetime.datetime(2020, 5, 18),
    },
}

user_data = {
    1: {
        "user_id": 1,
        "data": {
            "username": "new_username",
            "email": "new_email@example.com",
            "password": "new_password",
        },
    }
}

admin_data = {
    1: {"admin_id": 1, "data": {"username": "new_username", "password": "new_password"}}
}


user_reports = {
    1: {"user_id": 1, "job_id": 1, "data": {"report": "invalid link"}},
    2: {"user_id": 2, "job_id": 2, "data": {"report": "job is closed"}},
    3: {"user_id": 3, "job_id": 3, "data": {"report": "page not found"}},
}

user_preference = {
    1: {"user_id": 1, "location": "string", "job_type": "string", "sort_by": ["string"]}
}


def add_job_posting(company, job_title, job_description, job_type, location, date, link):
    if (
        company is None
        or job_title is None
        or job_description is None
        or job_type is None
        or location is None
        or date is None
        or link is None
    ):
        raise ValueError("None value found")
    return dbc.insert_one(
        "jobs",
        {
            "company": company,
            "job_title": job_title,
            "job_description": job_description,
            "job_type": job_type,
            "location": location,
            "date": date,
            "link": link
        },
    )


# def external_job_update(id, position, arg):
#     if id in job_data:
#         try:
#             job_data[id]["data"][position] = arg
#             return True
#         except Exception as e:
#             raise e
#     else:
#         raise KeyError("id not found")


def update_job(job_id, changes):
    """
    function to update the parameters of a job
    """
    if not dbc.exists_by_id(job_id, "jobs"):
        raise KeyError(f"No job {job_id}")
    return dbc.update_doc("jobs", {"_id": job_id}, changes)


def check_account(user_id, password):
    if not dbc.exists_by_id(user_id, "users"):
        raise KeyError(f"No User {user_id}")


def delete_job(admin_id, job_id):
    """finds job by _id and deletes it if possible"""
    if not dbc.exists_by_id(job_id, "jobs"):
        raise KeyError(f"No Job {job_id}")
    return dbc.del_one("jobs", {"_id": job_id})


def delete_job_past_date(admin_id, past_date):
    """flushes all entries past a date"""
    if not isinstance(past_date, datetime.datetime):
        raise TypeError("past_date must be datetime")
    for job in dbc.fetch_all("jobs"):
        if job["date"] < past_date:
            dbc.del_one("jobs", {"_id": job["_id"]})
    return True


def get_most_recent_job(numbers):
    # connect to mongodb to get the numbers of jobs based
    # on their date and store it into job list
    # jobs is a dictionary, key is date
    # jobs = dbc.fetch_all_as_dict("date", "jobs")
    # print(jobs[0][])
    jobs = dbc.fetch_elements_ordered_by("jobs", "date", limit=numbers)
    # find the most recent numbers of jobs based on key
    # last_keys = sorted_key[-numbers:]
    res = [job for job in jobs]
    print(res)
    for entry in res:
        entry["date"] = str(entry["date"].date())
        del entry["_id"]
    # print(res)
    return res[::-1]


def add_account(username, email, password):
    """
    function to add new account
    """
    exist = dbc.fetch_one("users", {"username": username})
    exist = exist or dbc.fetch_one("users", {"email": email})
    if exist:
        raise KeyError("User with Username or email already exists")
    else:
        return dbc.insert_one(
            "users",
            {
                "username": username,
                "email": email,
                "password": password,
                "preference": {"location": "any", "job_type": "any"},
            },
        )


def get_jobs_by_preference(preference):
    """
    function to get jobs based on user preference
    """
    if (
        not isinstance(preference, dict)
        or "location" not in preference
        or "job_type" not in preference
    ):
        raise TypeError(
            "preference must be a dictionary with\
                        'location' and 'job_type' keys"
        )
    all = dbc.fetch_all("jobs")
    return_list = []
    for job in all:
        job_copy = deepcopy(job)
        job_copy["_id"] = str(job_copy["_id"])
        job_copy["date"] = str(job_copy["date"])

        if job_copy not in return_list:
            if (
                preference["location"] == "any"
                or job_copy["location"] == preference["location"]
            ) and (
                preference["job_type"] == "any"
                or job_copy["job_type"] == preference["job_type"]
            ):
                return_list.append(job_copy)
    return return_list


def update_preference(user_id, preferred_location, preferred_type):
    if not dbc.exists_by_id(user_id, "users"):
        raise KeyError(f"No User {user_id}")
    return dbc.update_doc(
        "users",
        {"_id": user_id},
        {"preference": {"location": preferred_location, "job_type": preferred_type}},
    )


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
    return dbc.fetch_all("user_reports")


def add_user_report(user_id, job_id, report):
    """
    function to add a user report
    """
    if not dbc.exists_by_id(user_id, "users"):
        raise KeyError(f"No User {user_id}")
    if not dbc.exists_by_id(job_id, "jobs"):
        raise KeyError(f"No Job {job_id}")

    return dbc.insert_one(
        "user_reports",
        {"user_id": user_id, "job_id": job_id, "data": {"report": report}},
    )


def check_preference(user_id):
    """
    function to check and return current user preference
    """
    if not dbc.exists_by_id(user_id, "users"):
        raise KeyError(f"No User {user_id}")
    else:
        user = dbc.fetch_one("users", {"_id": user_id})
        return user["preference"]


def delete_user_report(report_id):
    """
    function to delete a user report
    """
    if not dbc.exists_by_id(report_id, "user_reports"):
        raise KeyError(f"No Report_ID {report_id}")
    return dbc.del_one("user_reports", {"_id": report_id})


def get_user_id(username, password):
    user = dbc.fetch_one("users", {"username": username})
    print(user)
    if user:
        if user["password"] == password:
            return user["_id"]
        else:
            return False
    else:
        return False


# if __name__ == "__main__":
#     add_account("test", "test@gmail.com", "test")
