"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from http import HTTPStatus
from bson.objectid import ObjectId
from flask import Flask, request
from flask_restx import Resource, Api
# from flask_restx import Resource, Api, fields

import werkzeug.exceptions as wz

import db.db as db
from datetime import datetime, date
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
DELETE_USER_REPORT = "delete_user_report"


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


@api.route(f'/{UPDATE_USER_INFO}')
class UpdateUserInfo(Resource):
    """
    This endpoint allows updating a user's information.
    """

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    @api.doc(params={
        '_id': {
            'description': 'User ID',
            'type': 'string',
            'default': "Test1",
        },
        'changes': {
            'email': {
                'description': 'Email',
                'type': 'string',
                'default': "Test2",
                'required': False
            },
            'username': {
                'description': 'Username',
                'type': 'string',
                'default': "Test3",
                'required': False
            },
        }
    })
    def put(self):
        user_id = request.json.get("_id")
        changes = request.json.get("changes")
        try:
            db.update_account(user_id, changes)
        except Exception as e:
            raise wz.NotAcceptable(str(e))

        return {"status": "success",
                "message": f"User {user_id} info updated"}, 200


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
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    @api.doc(params={
        'user_id': {
            'description': 'User ID',
            'type': 'string',
            'default': "Test1"
        },
        'job_id': {
            'description': 'Job ID',
            'type': 'string',
            'default': "Test2"
        },
        'report': {
            'description': 'report',
            'type': 'string',
            'default': "Test3"
        }
    })
    def post(self):
        user_id = request.json.get("user_id")
        if user_id is None:
            raise wz.NotAcceptable("Expected json with user_ID")
        job_id = request.json.get("job_id")
        if job_id is None:
            raise wz.NotAcceptable("Expected json with job_ID")
        report = request.json.get("report")
        try:
            db.add_user_report(user_id, job_id, report)
            return {"status": "success", "message":
                    "User report successfully submitted report"}, 200
        except Exception as e:
            raise wz.NotAcceptable(str(e))


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

        for res in response:
            res['_id'] = str(res['_id'])
            res['user_id'] = str(res['user_id'])
        return {"User Reports": response}, 200


@api.route(f'/{UPDATE_JOB_POSTING}')
class UpdateJobPosting(Resource):
    """
    This class allows admin accounts to update job postings
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    @api.doc(params={
        'job_id': {'description': 'Job ID', 'type': 'string'},

        'company': {'description': 'Company Name',
                    'type': 'string'
                    },
        'job_title': {'description': 'Job Title',
                      'type': 'string'
                      },
        'job_description': {'description': 'Job Description',
                            'type': 'string'
                            },
        'job_type': {'description': 'Job Type', 'type': 'string'
                     },
        'location': {'description': 'Location',  'type': 'string'
                     },
        'date': {'description': 'Date', 'type': str
                 }

    })
    def put(self):
        """
        updates job postings
        """
        job_id = request.args.get("job_id")
        if job_id is None:
            raise wz.NotAcceptable("Expected job_id")

        company = request.args.get("company")
        job_title = request.args.get("job_title")
        job_description = request.args.get("job_description")
        job_type = request.args.get("job_type")
        location = request.args.get("location")
        date = request.args.get("date")
        date_obj = None
        if date is not None:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
            except Exception as e:
                raise wz.NotAcceptable(str(e))

        try:
            job_id = ObjectId(job_id)
            print("error here?")
            changes = {'company': company, 'job_title': job_title,
                       'job_description': job_description,
                       'job_type': job_type, 'location': location,
                       'date': date_obj}
            fields = list(changes.keys())
            for field in fields:
                if changes[field] is None:
                    del changes[field]
            print("got here 1")
            db.update_job(job_id, changes)
            print("got here 2")
        except Exception as e:
            raise wz.NotAcceptable(str(e))

        return {"status": "success", "message": "Job posting updated"}, 200


@api.route(f'/{DELETE_ACCOUNT}')
class DeleteAccount(Resource):
    """
    This class allows users to delete their account
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    @api.doc(params={
        'user_id': {'description': 'User ID is not publicly facing',
                    'type': 'string', 'default': "Test1"
                    },
    })
    def delete(self):
        user_id = request.json.get("user_id")
        try:
            db.delete_account(ObjectId(user_id))
            return {"message": f"Successfully deleted {user_id}"}
        except Exception as e:
            raise wz.NotAcceptable(str(e))


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
    @api.doc(params={
        'username': {'description': 'Username',
                     'type': 'string', 'default': "Test1"
                     },
        'email': {'description': 'Email',
                  'type': 'string', 'default': "Test2"
                  },
        'password': {'description': 'Password',
                     'type': 'string', 'default': "Test3"
                     }
    })
    def put(self):
        """
        create new account
        """
        username = request.args.get("username")
        email = request.args.get("email")
        password = request.args.get("password")
        try:
            db.add_account(username, email, password)
            return {"status": "success",
                    "message": f"Account {username} successfully created"}, 200
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f'/{UPDATE_PREFERENCES}')
class Update_preferences(Resource):
    """
    This class allows users to update their account preferences
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not Acceptable')
    @api.doc(params={
        'user_id': {'description': 'User ID',
                    'type': 'string', 'default': "Test1"
                    },
        'location': {'description': 'Location',
                     'type': 'string', 'default': "Test2"
                     },
        'job_type': {'description': 'Job Type',
                     'type': 'string', 'default': "Test3"
                     },
        'sort_by': {'description': 'Sort By (Latest/Trending)',
                    'type': 'string', 'default': "Test4"
                    }
    })
    def put(self):
        """
        updates account preferences
        """
        user_id = request.json.get("user_id")
        location = request.json.get("preferred_location")
        job_type = request.json.get("preferred_job_type")
        sort_by = request.json.get("sort_by")
        try:
            db.update_preference(user_id, location, job_type, sort_by)
            return {"status": "success",
                    "message": "Account preference successfully updated"}, 200
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f'/{LOGIN_TO_ACCOUNT}')
class Login(Resource):
    """
    This class allows users to login to account
    """
    # @api.expect(api.model('LoginRequest', {
    #     "user_id": fields.String(required=True, description='user_id'),
    #     "password": fields.String(required=True, description='data')
    # }))
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
                     'date': {'description': 'Date', 'type': str,
                              'default': str(date.today().isoformat())}
                     })
    def post(self):
        company = request.args.get("company")
        job_title = request.args.get("job_title")
        job_description = request.args.get("job_description")
        job_type = request.args.get("job_type")
        location = request.args.get("location")
        date = request.args.get("date")
        if date is None:
            date = str(date.today().isoformat())
        date_obj = None
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
        except Exception as e:
            raise wz.NotAcceptable(str(e))

        # date =
        db.add_job_posting(company, job_title,
                           job_description, job_type, location, date_obj)
        # print(company, job_title, job_description, job_type, location)

        # return 200
        return {"status": "success", "message":
                "job posting successfully submit"}, 200


@api.route(f'/{DELETE_USER_REPORT}')
class DeleteUserReport(Resource):
    def post():
        report_id = request.args.get("report_id")
        db.delete_user_report(report_id)
        return "Successfully deleted", 400
