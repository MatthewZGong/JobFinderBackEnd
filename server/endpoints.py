"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from http import HTTPStatus
from bson.objectid import ObjectId
from flask import Flask, request
from flask_restx import Resource, Api
from flask_cors import CORS

# from flask_restx import Resource, Api, fields

import werkzeug.exceptions as wz

import db.db as db
from datetime import datetime, date

app = Flask(__name__)
CORS(app)
api = Api(app)

MAIN_MENU = "MainMenu"
MAIN_MENU_NM = "Welcome to Text Game!"
USERS = "users"

"""
ENDPOINTS
"""
UPDATE_USER_INFO = "UpdateUserInfo"
ADD_NEW_JOBS = "add-new-job"
USER_REPORT = "add-user-report"
GET_USER_REPORTS = "get-user-reports"
DELETE_ACCOUNT = "delete-account"
UPDATE_JOB_POSTING = "update-job-posting"
CREATE_USER_ACCOUNT = "create-account"
UPDATE_PREFERENCES = "update-preferences"
READ_MOST_RECENT_JOBS = "read_most_recent_jobs"
ADMIN_DELETE_JOBS = "admin_delete_jobs"
ADMIN_DELETE_PAST_DATE = "admin_delete_past_date"
DELETE_USER_REPORT = "delete_user_report"
GET_JOBS_BASED_ON_PREFERENCE = "get_job_based_on_preference"
HELLO_EP = "/hello-world"
HELLO_RESP = "HELLO WORLD"


@api.route(HELLO_EP)
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
        return {HELLO_RESP: "HELLO But with CORS"}


@api.route("/endpoints")
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


@api.route(f"/{UPDATE_USER_INFO}")
class UpdateUserInfo(Resource):
    """
    This endpoint allows updating a user's information.
    """

    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    @api.doc(
        params={
            "_id": {"description": "User ID", "type": "string", "default": "Test1", },
            "email": {
                "description": "Email",
                "type": "string",
                "default": "Test2",
                "required": False,
            },
            "username": {
                "description": "Username",
                "type": "string",
                "default": "Test3",
                "required": False,
            },
        }
    )
    def put(self):
        user_id = request.args.get("_id")
        if user_id is None:
            raise wz.NotAcceptable("Expected json with user_ID")
        email = request.args.get("email")
        if email is None:
            raise wz.NotAcceptable("Expected json with email")
        username = request.args.get("username")
        if username is None:
            raise wz.NotAcceptable("Expected json with username")
        new_email = request.args.get("new_email")
        new_username = request.args.get("new_username")
        changes = {"email": new_email, "username": new_username}
        try:
            db.update_account(ObjectId(user_id), changes)
        except Exception as e:
            raise wz.NotAcceptable(str(e))

        return {"status": "success", "message": f"User {user_id} info updated"}, 200


@api.route(f"/{USER_REPORT}")
class UserReport(Resource):
    """
    This class supports user to send in reports about job postings
    """

    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    @api.doc(
        params={
            "user_id": {"description": "User ID", "type": "string", "default": "Test1"},
            "job_id": {"description": "Job ID", "type": "string", "default": "Test2"},
            "report": {"description": "report", "type": "string", "default": "Test3"},
        }
    )
    def post(self):
        user_id = request.args.get("user_id")
        if user_id is None:
            raise wz.NotAcceptable("Expected json with user_ID")
        job_id = request.args.get("job_id")
        if job_id is None:
            raise wz.NotAcceptable("Expected json with job_ID")
        report = request.args.get("report")
        try:
            db.add_user_report(user_id, job_id, report)
            return (
                {
                    "status": "success",
                    "message": "User report successfully submitted report",
                },
                200,
            )
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f"/{GET_USER_REPORTS}")
class GetUserReports(Resource):
    """
    This class allows admin accounts to get User Reports
    """

    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    def get(self):
        """
        returns all user reports
        """
        response = db.get_user_reports()

        for res in response:
            res["_id"] = str(res["_id"])
            res["user_id"] = str(res["user_id"])
        return {"User Reports": response}, 200


@api.route(f"/{UPDATE_JOB_POSTING}")
class UpdateJobPosting(Resource):
    """
    This class allows admin accounts to update job postings
    """

    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    @api.doc(
        params={
            "job_id": {"description": "Job ID", "type": "string"},
            "company": {"description": "Company Name", "type": "string"},
            "job_title": {"description": "Job Title", "type": "string"},
            "job_description": {"description": "Job Description", "type": "string"},
            "job_type": {"description": "Job Type", "type": "string"},
            "location": {"description": "Location", "type": "string"},
            "date": {"description": "Date", "type": str},
        }
    )
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
                date_obj = datetime.strptime(date, "%Y-%m-%d")
            except Exception as e:
                raise wz.NotAcceptable(str(e))

        try:
            job_id = ObjectId(job_id)
            changes = {
                "company": company,
                "job_title": job_title,
                "job_description": job_description,
                "job_type": job_type,
                "location": location,
                "date": date_obj,
            }
            changes = filter(lambda x: changes[x] is not None, changes)

            db.update_job(job_id, changes)
        except Exception as e:
            print(e)
            raise wz.NotAcceptable(str(e))

        return {"status": "success", "message": "Job posting updated"}, 200


@api.route(f"/{DELETE_ACCOUNT}")
class DeleteAccount(Resource):
    """
    This class allows users to delete their account
    """

    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    @api.doc(
        params={
            "user_id": {
                "description": "User ID is not publicly facing",
                "type": "string",
                "default": "Test1",
            },
        }
    )
    def delete(self):
        user_id = request.args.get("user_id")
        try:
            db.delete_account(ObjectId(user_id))
            return {"message": f"Successfully deleted {user_id}"}
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f"/{READ_MOST_RECENT_JOBS}")
class read_most_recent_jobs(Resource):
    """
    This endpoint allows getting most recent jobs.
    """

    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    @api.doc(
        params={"numbers": {"description": "amount", "type": "int", "default": 5}, }
    )
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


@api.route(f"/{GET_JOBS_BASED_ON_PREFERENCE}")
class get_job_based_on_preference(Resource):
    """
    This endpoint allows getting jobs by user preference
    """

    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    @api.doc(
        params={
            "user_id": {
                "description": "User ID is not publicly facing",
                "type": "string",
                "default": "Test1",
            },
        }
    )
    def get(self):
        user_id = request.args.get("user_id")
        try:
            preference = db.check_preference(ObjectId(user_id))
            jobs = db.get_jobs_by_preference(preference)
            return {"Jobs": jobs}, 200
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f"/{ADMIN_DELETE_JOBS}")
class admin_delete_jobs(Resource):
    """
    This endpoint allows deleting the expired jobs based on job_id.
    """

    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    @api.doc(
        params={
            "admin_id": {
                "description": "Admin ID",
                "type": "string",
                "default": "Test1",
            },
            "job_id": {"description": "Job ID", "type": "string", "default": "Test2"},
        }
    )
    def delete(self):
        admin_id = request.args.get("admin_id")
        if admin_id is None:
            raise wz.NotAcceptable("Expected json with admin_ID")
        job_id = request.args.get("job_id")
        if job_id is None:
            raise wz.NotAcceptable("Expected json with job_ID")

        try:
            db.delete_job(admin_id, ObjectId(job_id))
            return {"status": "success", "message": f"Job {job_id} deleted"}, 200
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f"/{ADMIN_DELETE_PAST_DATE}")
class admin_delete_past_date(Resource):
    """
    This endpoint allows admin to delete all entries in the past certain date.
    """

    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    @api.doc(
        params={
            "admin_id": {
                "description": "User ID",
                "type": "string",
                "default": "Test1",
            },
            "invalid_past_date": {
                "description": "Invalid Past Date",
                "type": "datetime",
                "default": "Test2",
            },
        }
    )
    def delete(self):
        admin_id = request.args.get("admin_id")
        if admin_id is None:
            raise wz.NotAcceptable("Expected json with admin_ID")
        try:
            invalid_past_date_s = request.args.get("invalid_past_date")
            invalid_past_date = datetime.strptime(invalid_past_date_s, "%Y-%m-%d")
            db.delete_job_past_date(admin_id, invalid_past_date)
            return {"status": "success", "message": "Jobs deleted"}, 200
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f"/{CREATE_USER_ACCOUNT}")
class CreateAccount(Resource):
    """
    This class allows users to create an account
    """

    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    @api.doc(
        params={
            "username": {
                "description": "Username",
                "type": "string",
                "default": "Test1",
            },
            "email": {"description": "Email", "type": "string", "default": "Test2"},
            "password": {
                "description": "Password",
                "type": "string",
                "default": "Test3",
            },
        }
    )
    def put(self):
        """
        create new account
        """
        username = request.args.get("username")
        email = request.args.get("email")
        password = request.args.get("password")
        try:
            db.add_account(username, email, password)
            return (
                {
                    "status": "success",
                    "message": f"Account {username} successfully created",
                },
                200,
            )
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f"/{UPDATE_PREFERENCES}")
class Update_preferences(Resource):
    """
    This class allows users to update their account preferences
    """

    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    @api.doc(
        params={
            "user_id": {"description": "User ID", "type": "string"},
            "location": {"description": "Location", "type": "string", "default": "any"},
            "job_type": {"description": "Job Type", "type": "string", "default": "any"},
        }
    )
    def put(self):
        """
        updates account preferences
        """
        user_id = request.args.get("user_id")
        password = request.args.get("password")
        location = request.args.get("location")
        job_type = request.args.get("job_type")
        try:
            db.check_account(ObjectId(user_id), password)
            db.update_preference(ObjectId(user_id), location, job_type)
            return (
                {
                    "status": "success",
                    "message": "Account preference successfully updated",
                },
                200,
            )
        except Exception as e:
            raise wz.NotAcceptable(str(e))


@api.route(f"/{ADD_NEW_JOBS}")
class AddNewJobPosting(Resource):
    """
    This class supports user to send in reports about job postings
    """

    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    @api.doc(
        params={
            "company": {
                "description": "Company Name",
                "type": "string",
                "default": "Test1",
            },
            "job_title": {
                "description": "Job Title",
                "type": "string",
                "default": "Test2",
            },
            "job_description": {
                "description": "Job Description",
                "type": "string",
                "default": "Test3",
            },
            "job_type": {
                "description": "Job Type",
                "type": "string",
                "default": "Test4",
            },
            "location": {
                "description": "Location",
                "type": "string",
                "default": "Test5",
            },
            "date": {
                "description": "Date",
                "type": str,
                "default": str(date.today().isoformat()),
            },
        }
    )
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
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except Exception as e:
            raise wz.NotAcceptable(str(e))
        # date =
        db.add_job_posting(
            company, job_title, job_description, job_type, location, date_obj
        )
        return {"status": "success", "message": "job posting successfully submit"}, 200


@api.route(f"/{DELETE_USER_REPORT}")
class DeleteUserReport(Resource):
    @api.response(HTTPStatus.OK, "Success")
    @api.response(HTTPStatus.NOT_ACCEPTABLE, "Not Acceptable")
    @api.doc(
        params={
            "report_id": {
                "description": "User Report ID",
                "type": "string",
                "default": "Test1",
            }
        }
    )
    def delete(self):
        report_id = request.args.get("report_id")
        try:
            db.delete_user_report(ObjectId(report_id))
        except Exception as e:
            raise wz.NotAcceptable(str(e))
        return "Successfully deleted", 200
