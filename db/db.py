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
                "email": "new_email@example.com"
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

def external_job_update(id, position, arg):
    if id in job_data:
        try:
            job_data[id]["data"][position] = arg
            return True
        except Exception as e:
            raise e
    else:
        raise KeyError("id not found")


def delete_job(job_id):
    # connect to sql to find the jobs corresponding to this
    # job name and delete it, return 1 if suffcessfull deleted, 0 if fail
    if job_id in job_data:
        try:
            #del job_data[job_id]
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


def check_account():
    """
    Check whether password/username pair matches an entry in db.
    """
    return True
