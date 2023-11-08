"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
"""
data = {
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


def external_job_update(id, position, arg):
    if id in data:
        try:
            data[id]["data"][position] = arg
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
