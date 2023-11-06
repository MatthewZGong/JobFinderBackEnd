"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from flask import Flask, request
from flask_restx import Resource, Api

# import db.db as db

app = Flask(__name__)
api = Api(app)

MAIN_MENU = 'MainMenu'
MAIN_MENU_NM = "Welcome to Text Game!"
USERS = 'users'

"""
ENDPOINTSs
"""
UPDATE_USER_INFO = 'UpdateUserInfo'
UPDATE_AVAILABLE_JOBS = 'UpdateAvailableJobs'
KEYWORD_SEARCH = 'Keyword_Search'
USER_REPORT = "userreport"
GET_USER_REPORTS = "get-user-reports"
DELETE_ACCOUNT = "delete-account"
UPDATE_JOB_POSTING = "update-job-posting"
CREATE_USER_ACCOUNT = "create-account"
LOGIN_TO_ACCOUNT = "login-to-account"
UPDATE_PREFERENCES = "update-preferences"
READ_MOST_RECENT_JOBS = "read_most_recent_jobs"
ADMIN_DELETE_JOBS = "admin_delete_jobs"
ADMIN_DELETE_PAST_DATE = "admin_delete_past_date"


@api.route('/hello')
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        It just answers with "hello world."
        """
        return {'hello': 'world'}


@api.route('/endpoints')
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route(f'/{MAIN_MENU}')
@api.route('/')
class MainMenu(Resource):
    """
    This will deliver our main menu.
    """
    def get(self):
        """
        Gets the main game menu.
        """
        return {'Title': MAIN_MENU_NM,
                'Default': 2,
                'Choices': {
                    '1': {'url': '/', 'method': 'get',
                          'text': 'List Available Characters'},
                    '2': {'url': '/',
                          'method': 'get', 'text': 'List Active Games'},
                    '3': {'url': f'/{USERS}',
                          'method': 'get', 'text': 'List Users'},
                    'X': {'text': 'Exit'},
                }}


@api.route(f'/{USERS}')
class Users(Resource):
    """
    This class supports fetching a list of all pets.
    """
    def get(self):
        """
        This method returns all users.
        """
        return 'Current Users:\nSai\nAbhishek\nKristian\n'


@api.route(f'/{UPDATE_USER_INFO}')
class UpdateUserInfo(Resource):
    """
    This endpoint allows updating a user's information.
    """
    Users = set([1, 2, 3, 4])

    def put(self):
        user_id = request.json.get("user_id")
        # data = request.json.get("data")
        if (user_id not in UpdateUserInfo.Users):
            return {"status": "failure", "message":
                    "Invalid User ID"}, 400

        return {"status": "success",
                "message": f"User {user_id} info updated"}, 200


@api.route(f'/{UPDATE_AVAILABLE_JOBS}')
class UpdateAvailableJobs(Resource):
    """
    This endpoint updates the list of available jobs.
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

    def put(self):
        """
        Updates the list of available jobs based on input.
        Right now it does nothing and just returns success.
        """
        def external_job_update(id, position, arg):
            if id in UpdateAvailableJobs.data:
                UpdateAvailableJobs.data[id]["data"][position] = arg
                return True
            else:
                return False
        id = request.json.get("id")
        position = request.json.get("position")
        arg = request.json.get("arg")
        if external_job_update(id, position, arg):
            return {"status": "success", "message": f"Job {id} updated"}, 200
        return {"status": "failed", "message":
                f"Failed to update job {id}"}, 400


@api.route(f'/{KEYWORD_SEARCH}')
class KeywordSearchDatabase(Resource):
    """
    This endpoint performs a keyword search on the database.
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

    def get(self):
        """
        Searches the database for the given keyword and returns results.
        Right now it returns dummy data since we don't have a database.
        """

        keyword = request.json.get("keyword")
        results = []
        for i in KeywordSearchDatabase.data:
            entry = KeywordSearchDatabase.data[i]
            if keyword in entry["data"]["keywords"]:
                results.append(entry)
        return {"results": results}, 200


@api.route(f'/{USER_REPORT}')
class UserReport(Resource):
    """
    This class supports user to send in reports about job postings
    """
    Jobs = set([1, 2, 3, 4])
    Users = set([1, 2, 3, 4])

    def post(self):
        user_id = request.json.get("user_id")
        job_id = request.json.get("job_id")
        report = request.json.get("report")
        if (user_id not in UserReport.Users):
            return {"status": "failure", "message":
                    "Invalid User ID"}, 400
        if (job_id is not None and job_id not in UserReport.Jobs):
            return {"status": "failure", "message":
                    "Invalid Job Id"}, 400
        if (report is None or report == ""):
            return {"status": "failure", "message":
                    "Invalid report"}, 400

        return {"status": "success", "message":
                "User report successfully submitted report"}, 200


@api.route(f'/{GET_USER_REPORTS}')
class GetUserReports(Resource):
    """
    This class allows admin accounts to get User Reports
    """
    TempReport = [{"user_id": 1, "job_id": 1, "report": "invalid link"},
                  {"user_id": 2, "job_id": 2, "report": "job is closed"},
                  {"user_id": 3, "job_id": 3, "report": "page not found"},]

    def get(self):
        """
        returns all user reports
        """

        if request.json.get("user_id") != 1:
            return {"message":
                    "Invalid User ID"}, 400
        response = []
        for report in GetUserReports.TempReport:
            response.append(report)
        return {"User Reports": response}, 200


@api.route(f'/Admin/{UPDATE_JOB_POSTING}')
class UpdateJobPosting(Resource):
    """
    This class allows admin accounts to update job postings
    """
    def put(self):
        """
        updates job postings
        """
        return {"status": "success", "message": "Job posting updated"}, 200


@api.route(f'/{DELETE_ACCOUNT}')
class DeleteAccount(Resource):
    """
    This class allows users to delete their account
    """
    Temp_users = set([1, 2, 3, 4])

    def delete(self):
        # check if user is admin or not
        user_id = request.json.get("user_id")
        # check if user is in database
        if user_id is None or user_id not in DeleteAccount.Temp_users:
            return {"status": "failure",
                    "message": "Wrong Permission"}, 400
        # db not set up yet
        # make sure user sending is correct user and has correct permsission
        # do authentication that user deleting acount
        # is the same as user sending
        # make sure user is not admin user
        if user_id == 1:
            return {"status": "failure",
                    "message": "Wrong Permission"}, 400
        # db not set up yet
        # log out user
        return {"status": "success",
                "message": "Account successfully deleted"}, 200


@api.route(f'/{READ_MOST_RECENT_JOBS}')
class read_most_recent_jobs(Resource):
    """
    This endpoint allows getting most recent jobs.
    """
    def get(self):
        numbers = request.json.get("numbers")
        numbers = numbers
        # connect to sql to get the X number of jobs based
        # on their date and store it into job list
        return {"status": "success",
                "message":  "recent job successfully get"}, 200


@api.route(f'/{ADMIN_DELETE_JOBS}')
class admin_delete_jobs(Resource):
    """
    This endpoint allows deleting the expired jobs based on job_name.
    """

    def delete(self):
        job_name = request.json.get("invalid_job")
        job_name = job_name
        # connect to sql to find the jobs corresponding to this
        # job name and delete it, return 1 if suffcessfull deleted, 0 if fail
        res = 1
        if res == 1:
            return {"status": "success",
                    "message": "bad job successfully deleted"}, 200
        else:
            return {"status": "fail",
                    "message": "deleted fail"}, 200


@api.route(f'/{ADMIN_DELETE_PAST_DATE}')
class admin_delete_past_date(Resource):
    """
    This endpoint allows admin to delete all entries in the past certain date.
    """
    def delete(self):
        past_certain_date = request.json.get("past_certain_date")
        past_certain_date = past_certain_date
        # connect to the sql and delete the jobs before the past_certain_date
        # eg: DELETE FROM jobs where release_date<past_certain_date
        # return 1 if successfully deleted
        # return 0 if some errors occured
        res = 1
        if res == 1:
            return {"status": "success",
                    "message": "past date jobs successfully deleted"}, 200
        else:
            return {"status": "fail",
                    "message": "deleted fail"}, 200


@api.route(f'/{CREATE_USER_ACCOUNT}')
class CreateAccount(Resource):
    """
    This class allows users to create an account
    """
    def create(self):
        name = request.json.get("name")
        email = request.json.get("email")
        # check if email is associated with an existing account,
        # if no, get password and create account
        password = request.json.get("password")
        name = name
        email = email
        password = password
        information = {"name": name,
                       "email/userid": email,
                       "password": password}
        if information != 1:
            return {"status": "failure",
                    "message": "Fail to create account"}, 200
        return {"status": "success",
                "message": "Account successfully created"}, 200


@api.route(f'/{UPDATE_PREFERENCES}')
class Update_preferences(Resource):
    """
    This class allows users to update their account preferences
    """
    def update(self):
        return {"status": "success",
                "message": "Preferences Successfully Updated"}, 200


@api.route(f'/{LOGIN_TO_ACCOUNT}')
class Login(Resource):
    """
    This class allows users to login to account
    """
    def login(self):
        password = request.json.get("password")
        email = request.json.get("email")
        password = password
        email = email
        # check if the password-email combination matches with a entry in db.
        # If yes, login and return login success
        if email != 1:
            return {"message": "Invalid User ID/Email"}, 400
        return {"status": "success", "message": "Successfully Logged In"}, 200
