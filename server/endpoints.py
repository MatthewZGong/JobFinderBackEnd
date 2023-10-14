"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from flask import Flask
from flask_restx import Resource, Api
# import db.db as db

app = Flask(__name__)
api = Api(app)

MAIN_MENU = 'MainMenu'
MAIN_MENU_NM = "Welcome to Text Game!"
USERS = 'users'
UPDATE_USER_INFO = 'UpdateUserInfo'
UPDATE_AVAILABLE_JOBS = 'UpdateAvailableJobs'
KEYWORD_SEARCH = 'Keyword_Search'


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
    def put(self, user_id):
        """
        Updates the specified user's information based on input.
        For the sake of the skeleton, it does nothing and just returns success.
        """

        return {"status": "success", "message": "User info updated"}, 200


@api.route(f'/{UPDATE_AVAILABLE_JOBS}')
class UpdateAvailableJobs(Resource):
    """
    This endpoint updates the list of available jobs.
    """
    def put(self):
        """
        Updates the list of available jobs based on input.
        Right now it does nothing and just returns success.
        """

        return {"status": "success", "message": "Jobs updated"}, 200


@api.route(f'/{KEYWORD_SEARCH}')
class KeywordSearchDatabase(Resource):
    """
    This endpoint performs a keyword search on the database.
    """
    def get(self, keyword):
        """
        Searches the database for the given keyword and returns results.
        Right now it returns dummy data.
        """

        dummy_results = [{"id": 1, "name": "Sample Data 1"},
                         {"id": 2, "name": "Sample Data 2"}]
        return {"results": dummy_results}, 200
