import db.db_connect as dbc
import datetime
import openai
import time
import random
import os


"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
"""


# import db_connect as dbc
# print(__name__)
dbc.connect_db()
open_ai_client = None
if os.environ.get("OPENAI_API_KEY") is not None:
    open_ai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

DEFAULT_VECTOR = [0.0000001] * 1536

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


def add_job_posting(company, job_description, job_type, location, date, link):
    '''
    company: the company name
    job_description: the job description
    job_type: the job type
    location: the location
    date: the date
    link: the link
    This function adds a new job posting to the database.
    '''
    if (
        company is None
        or job_type is None
        or location is None
        or date is None
        or link is None
    ):
        raise ValueError("None value found")
    vector = generate_vector(
        company
        + " "
        + location
        + " "
        + job_type
        + " "
        + date.strftime("%Y-%m-%d")
        + " "
        + job_description
    )
    return dbc.insert_one(
        "jobs",
        {
            "company": company,
            "job_description": job_description,
            "job_type": job_type,
            "location": location,
            "date": date,
            "link": link,
            "embedding_vector": vector,
        },
    )


def update_job(job_id, changes):
    """
    function to update the parameters of a job
    """
    if not dbc.exists_by_id(job_id, "jobs"):
        raise KeyError(f"No job {job_id}")
    res = dbc.update_doc("jobs", {"_id": job_id}, changes)
    if not res:
        raise KeyError(f"No job {job_id}")
    job = dbc.fetch_one("jobs", {"_id": job_id})
    vector = generate_vector(
        job.setdefault("company", "")
        + " "
        + job.setdefault("location", "")
        + " "
        + job.setdefault("job_type", "")
        + " "
        + job.setdefault("date", datetime.datetime.now()).strftime("%Y-%m-%d")
        + " "
        + job.setdefault("job_description", "")
    )
    del job["_id"]
    job["embedding_vector"] = vector
    dbc.update_doc("jobs", {"_id": job_id}, job)
    return res


def check_account(user_id, password):
    '''
    user_id: the user id to be checked
    this function checks if a user exists in the database.
    '''
    if not dbc.exists_by_id(user_id, "users"):
        raise KeyError(f"No User {user_id}")


def delete_job(admin_id, job_id):
    """finds job by _id and deletes it if possible"""
    if not dbc.exists_by_id(job_id, "jobs"):
        raise KeyError(f"No Job {job_id}")
    return dbc.del_one("jobs", {"_id": job_id})


def delete_job_past_date(past_date):
    """flushes all entries past a date"""
    if not isinstance(past_date, datetime.datetime):
        raise TypeError("past_date must be datetime")
    for job in dbc.fetch_all("jobs"):
        if job["date"] < past_date:
            dbc.del_one("jobs", {"_id": job["_id"]})
    return True


def get_most_recent_job(numbers):
    '''
    numbers: the number of jobs to return
    This function fetches the most recent jobs based on the number of jobs provided.
    The jobs are fetched from the database using the "jobs" collection.
    The jobs are fetched from the database using the "jobs" collection.
    '''
    jobs = dbc.fetch_elements_ordered_by("jobs", "date", limit=numbers)
    res = [job for job in jobs]
    for entry in res:
        entry["date"] = str(entry["date"].date())
        entry["job_id"] = str(entry["_id"])
        del entry["_id"]
        del entry["embedding_vector"]
    # print(res)
    return res


def add_account(username, email, password):
    """
    function to add new account
    """
    exist = dbc.fetch_one("users", {"username": username})
    if exist:
        raise KeyError("Username already exists")
    exist1 = dbc.fetch_one("users", {"email": email})
    if exist1:
        raise KeyError("User's Email already exists")
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
    '''
    username: the username to be fetched
    password: the password to be used to authenticate the user
    This function fetches the user ID of a user based on its username and password.
    '''
    user = dbc.fetch_one("users", {"username": username})
    print(user)
    if user:
        if user["password"] == password:
            return user["_id"]
        else:
            return False
    else:
        return False


def get_username_by_id(user_id):
    '''
    user_id: the user id to be fetched
    This function fetches the username of a user based on its ID.
    '''
    user = dbc.fetch_one("users", {"_id": user_id})
    if user:
        return user["username"]
    else:
        return False


def get_job_by_id(job_id):
    '''
    job_id: the job id to be fetched
    This function fetches a job based on its ID.
    '''
    job = dbc.fetch_one("jobs", {"_id": job_id})
    if job:
        job["_id"] = str(job["_id"])
        job["date"] = str(job["date"])
        return job
    else:
        return False


def generate_vector(text):
    '''
    text: the text to be embedded
    This function generates a vector of job descriptions using the OpenAI.
    The vector is generated using the OpenAI text-embedding-ada-002 model.
    '''
    # print(os.environ.get("OPENAI_API_KEY"))
    if open_ai_client is None:
        return DEFAULT_VECTOR
    attempt = 0
    while True:
        try:
            response = open_ai_client.embeddings.create(
                input=text, model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except openai.RateLimitError:
            attempt += 1
            wait_time = min(2 ** attempt + random.random(), 60)
            if attempt == 10:
                break
            time.sleep(wait_time)
        except Exception:
            break
    return DEFAULT_VECTOR


def search_jobs_by_vector(text, limit=10):
    '''
    text: the search query
    limit: the number of jobs to return
    This function searches for jobs based on a vector of job descriptions.
    The vector is generated from the text provided.
    then the vector is passed into mongodb to search for jobs that match the vector.
    Returns jobs that matches the search query.
    '''
    vector = generate_vector(text)
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding_vector",
                "queryVector": vector,
                "numCandidates": limit * 3,
                "limit": limit,
            }
        }
    ]
    cursor = dbc.aggregate_job(pipeline)
    # print("HI I GOT HERE 3")
    results = [
        {
            "job_id": str(result["_id"]),
            "company": result["company"],
            "job_description": result["job_description"],
            "job_type": result["job_type"],
            "location": result["location"],
            "date": str(result["date"].date()),
            "link": result["link"],
        }
        for result in cursor
    ]
    return results


def re_embed_all_jobs():
    '''
    This function re-emebeds all jobs embeddings vectors in the database.
    '''
    jobs = dbc.fetch_all("jobs")
    for i, job in enumerate(jobs):
        job["embedding_vector"] = generate_vector(
            job["company"]
            + " "
            + job["location"]
            + " "
            + job["job_type"]
            + " "
            + job["date"].strftime("%Y-%m-%d")
            + " "
            + job["job_description"]
        )
        update_job(job["_id"], job)
        if i % 10 == 0:
            print(f"Re-embedding {i} jobs")


if __name__ == "__main__":
    re_embed_all_jobs()
    # add_account("test", "test@gmail.com", "test")
