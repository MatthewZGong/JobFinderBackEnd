"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
"""
job_data = {
        1: {
            "data": {
                "keywords": ["internship"]
            },
            "userid": 1
        },
        2: {
            "data": {
               "keywords": ["Remote"]
            },
            "userid": 2
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
    # connect to sql to find the jobs corresponding to this
    # job name and delete it, return 1 if suffcessfull deleted, 0 if fail
    if job_id in job_data and admin_id in admin_data:
        try:
            # del job_data[job_id]
            return True
        except Exception as e:
            raise e
    else:
        raise KeyError("id not found")


def get_most_recent_job(user_id, numbers):
    # connect to sql to get the numbers of jobs based
    # on their date and store it into job list
    if user_id in user_data:
        try:
            return True
        except Exception as e:
            raise e
    else:
        raise KeyError("id not found")


def fetch_pets():
    """
    A function to return all pets in the data store.
    """
    return {"tigers": 2, "lions": 3, "zebras": 1}


def check_account(user_id, user_password):
    """
    Check whether password/username pair matches an entry in db.
    """
    if user_id in user_data:
        if user_password == user_data[1]["data"]["password"]:
            return True
    return False


def get_user_reports():
    """
    function to fetch all user reports
    """
    return {}


def add_user_report():
    """
    function to add a user report
    """
    return True


def delete_user_report(user_id, report_id):
    """
    function to delete a user report
    """
    return True
