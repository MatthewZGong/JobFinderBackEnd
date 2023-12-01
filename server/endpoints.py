"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from http import HTTPStatus

from flask import Flask, request
from flask_restx import Resource, Api, fields

import werkzeug.exceptions as wz

import db.db as db
from datetime import datetime
app = Flask(__name__)
api = Api(app)

MAIN_MENU = 'MainMenu'
MAIN_MENU_NM = "Welcome to Text Game!"
USERS = 'users'

"""
ENDPOINTS
"""
UPDATE_USER_INFO = 'UpdateUserInfo'
ADD_NEW_JOBS = "add-new-job"
UPDATE_AVAILABLE_JOBS = 'UpdateAvailableJobs'
KEYWORD_SEARCH = 'Keyword_Search'
USER_REPORT = "add-user-report"
GET_USER_REPORTS = "get-user-reports"
DELETE_ACCOUNT = "delete-account"
UPDATE_JOB_POSTING = "update-job-posting"
CREATE_USER_ACCOUNT = "create-account"
LOGIN_TO_ACCOUNT = "login-to-account"
UPDATE_PREFERENCES = "update-preferences"
READ_MOST_RECENT_JOBS = "read_most_recent_jobs"
ADMIN_DELETE_JOBS = "admin_delete_jobs"
ADMIN_DELETE_PAST_DATE = "admin_delete_past_date"


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

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    def put(self):
        user_id = request.json.get("user_id")
        if user_id is None:
            raise wz.NotAcceptable("Invalid User_ID")
        if (user_id not in db.user_data):
            raise wz.NotAcceptable("Invalid User_ID")

        return {"status": "success",
                "message": f"User {user_id} info updated"}, 200


@api.route(f'/{UPDATE_AVAILABLE_JOBS}')
class UpdateAvailableJobs(Resource):
    """
    This endpoint updates the list of available jobs.
    """

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    def put(self):
        """
        Updates the list of available jobs based on input.
        Right now it does nothing and just returns success.
        """

        id = request.json.get("id")
        position = request.json.get("position")
        arg = request.json.get("args")
        if id is None or position is None or arg is None:
            raise wz.NotAcceptable("Expected json with ID, Position, Args")
        try:
            db.external_job_update(id, position, arg)
            return {"status": "success", "message": f"Job {id} updated"}, 200
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f'/{KEYWORD_SEARCH}')
class KeywordSearchDatabase(Resource):
    """
    This endpoint performs a keyword search on the database.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    def get(self):
        """
        Searches the database for the given keyword and returns results.
        Right now it returns dummy data since we don't have a database.
        """

        keyword = request.json.get("keyword")
        if keyword is None:
            raise wz.NotAcceptable("Keyword Needed")
        results = []
        for i in db.job_data:
            entry = db.job_data[i]
            if keyword in entry["data"]["keywords"]:
                entry_date = entry.get("date", "")
                if isinstance(entry_date, datetime):
                    entry["date"] = entry_date.isoformat()
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
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    def get(self):
        """
        returns all user reports
        """
        response = db.get_user_reports()
        print(response)
        for res in response:
            res['_id'] = str(res['_id'])
            res['user_id'] = str(res['user_id'])
        return {"User Reports": response}, 200


@api.route(f'/Admin/{UPDATE_JOB_POSTING}')
class UpdateJobPosting(Resource):
    """
    This class allows admin accounts to update job postings
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    @api.doc(params={'company': {'description': 'Company Name',
                                 'type': 'string', 'default': "Test1"
                                 },
                     'job_title': {'description': 'Job Title',
                                   'type': 'string', 'default': "Test2"
                                   },
                     'job_description': {'description': 'Job Description',
                                         'type': 'string', 'default': "Test3"
                                         },
                     'job_type': {'description': 'Job Type', 'type': 'string',
                                  'default': "Test4"
                                  },
                     'location': {'description': 'Location',  'type': 'string',
                                  'default': "Test5"
                                  },
                     })
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
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    @api.doc(params={'numbers': {'description': 'amount',
                                 'type': 'int', 'default': 5},
                     })
    def get(self):
        # user_id = request.json.get("user_id")
        # if user_id is None:
        #     raise wz.NotAcceptable("Expected json with user_ID")
        try:

            numbers = int(request.args.get("numbers"))
            res = db.get_most_recent_job(numbers)
            return res, 200
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f'/{ADMIN_DELETE_JOBS}')
class admin_delete_jobs(Resource):
    """
    This endpoint allows deleting the expired jobs based on job_id.
    """

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    @api.doc(params={'admin_id': {'description': 'Admin ID',
                                  'type': 'string', 'default': "Test1"},
                     'job_id': {'description': 'Job ID',
                                'type': 'string', 'default': "Test2"},
                     })
    def delete(self):
        admin_id = request.args.get("admin_id")
        if admin_id is None:
            raise wz.NotAcceptable("Expected json with admin_ID")
        job_id = request.args.get("job_id")
        if job_id is None:
            raise wz.NotAcceptable("Expected json with job_ID")

        try:
            db.delete_job(admin_id, job_id)
            return {"status": "success", "message": f"Job {job_id} deleted"},
            200
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f'/{ADMIN_DELETE_PAST_DATE}')
class admin_delete_past_date(Resource):
    """
    This endpoint allows admin to delete all entries in the past certain date.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    def delete(self):
        admin_id = request.json.get("admin_id")
        if admin_id is None:
            raise wz.NotAcceptable("Expected json with admin_ID")
        invalid_past_date = request.json.get("invalid_past_date")
        try:
            db.delete_job_past_date(admin_id, invalid_past_date)
            return {"status": "success", "message": "Jobs deleted"}, 200
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f'/{CREATE_USER_ACCOUNT}')
class CreateAccount(Resource):
    """
    This class allows users to create an account
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    def put(self):
        """
        create new account
        """
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
    @api.expect(api.model('UpdatePreferenceRequest', {
        "user_id": fields.String(required=True, description='user_id'),
        "location": fields.String(required=True, description='location'),
        "job_type": fields.String(required=True, description='type'),
        "sort_by": fields.String(required=True, description='sort_by')
    }))
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    def put(self):
        """
        updates account preferences
        """
        user_id = request.json.get("user_id")
        preferred_location = request.json.get("preferred_location")
        preferred_job_type = request.json.get("preferred_job_type")
        sort_by = request.json.get("sort_by")
        # connect to the sql and update users specific preference attribute
        # eg: update for user 1 jobs type from intern to full time
        # UPDATE users
        # set preference.job_type = full_time
        # where user_id = 1
        db.update_preference(user_id, location, job_type, sort_by)
        return {"status": "success",
                "message": "Preferences Successfully Updated"}, 200


@api.route(f'/{LOGIN_TO_ACCOUNT}')
class Login(Resource):
    """
    This class allows users to login to account
    """
    @api.expect(api.model('LoginRequest', {
        "user_id": fields.String(required=True, description='user_id'),
        "password": fields.String(required=True, description='data')
    }))
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    def put(self):
        """
        login to accounts
        """
        user_id = request.json.get("user_id")
        password = request.json.get("password")
        # username = request.json.get("username")
        # check if the password-email combination matches with a entry in db.
        # If yes, login and return login success
        if (user_id not in db.user_data):
            return {"message": f"Invalid User ID: {user_id}"}, 400
        else:
            if db.user_data[user_id]["data"]["password"] == password:
                return {"status": "success", "message": "Login Success"}, 200
            else:
                return {"message": "Invalid password"}, 400


@api.route(f'/{ADD_NEW_JOBS}')
class AddNewJobPosting(Resource):
    """
    This class supports user to send in reports about job postings
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    @api.doc(params={'company': {'description': 'Company Name',
                                 'type': 'string', 'default': "Test1"},
                     'job_title': {'description': 'Job Title',
                                   'type': 'string', 'default': "Test2"},
                     'job_description': {'description': 'Job Description',
                                         'type': 'string', 'default': "Test3"},
                     'job_type': {'description': 'Job Type', 'type': 'string',
                                  'default': "Test4"},
                     'location': {'description': 'Location',  'type': 'string',
                                  'default': "Test5"},
                     })
    def post(self):
        company = request.args.get("company")
        job_title = request.args.get("job_title")
        job_description = request.args.get("job_description")
        job_type = request.args.get("job_type")
        location = request.args.get("location")
        db.add_job_posting(company, job_title,
                           job_description, job_type, location)
        # print(company, job_title, job_description, job_type, location)

        # return 200
        return {"status": "success", "message":
                "job posting successfully submit"}, 200
