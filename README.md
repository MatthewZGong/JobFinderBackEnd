# Job Finder

Team members: Tanzir Hasan, Matthew Gong, Shao Jin, Michelle Lin

## Purpose

A job finder for adding/deleting and finding jobs of individual preferences. Serves as a personalized job finder where personal information and preferences are used. 

## Setup 

### Installation
The project is written in Python 3.9. To install the required packages, run the following command:

1. Clone the repository to your local machine.
2. It is recomended to use a virtual environment to install the packages. 
    - If you are using a virtual environment, activate it before running the following commands: `python -m venv venv; source venv/bin/activate`
    - If you are not using a virtual environment, you can skip this step.

3. run `make dev_env` to install the required packages, for dev enviroment.
    - you can run `make prod` for production enviroment.
4. run `./local.sh` to start the server locally.


### Environment variables
```
DB_NAME=
MONGO_USERNAME=
MONGO_PASSWORD=
CLOUD_MONGO=
OPENAI_API_KEY=
```
- DB_NAME: The name of the MongoDB database to connect to.
- MONGO_USERNAME: The username for the MongoDB database.
- MONGO_PASSWORD: The password for the MongoDB database.
- CLOUD_MONGO: Set to 1 if the database is hosted on a cloud provider, 0 if it is hosted on a local server.
- OPENAI_API_KEY: The API key for the OpenAI API.

It could be helpful to put these in a shell script and export them if there are problems with using a .env.

## What is this

This project defines a set of RESTful API endpoints for managing user accounts, job postings, and user reports related to job postings.

## Endpoints
### /endpoints

#### `GET`

- Returns a list of all available endpoints in the system.

### /update_user_info

#### `PUT`

- Allows updating a user's information. 

#### Parameters

- `_id` (string): User ID
- `new_email` (string): New email for the user
- `new_username` (string): New username for the user

### /add_user_report

#### `POST`

- Allows users to submit reports about job postings.

#### Parameters

- `user_id` (string): User ID submitting the report.
- `job_id` (string): ID of the job being reported.
- `report` (string): The user's report.

### /get_user_reports

#### `GET`

- Retrieve all user reports.

### /update_job_posting

#### `PUT`

- Used to update job postings description.

#### Parameters

- `job_id` (string): ID of the job to be updated.
- `company` (string): The company that posted the job
- `job_description` (string): Description of the job
- `job_type` (string): The type of job
- `location` (string): The location of the job
- `date` (string): The date of the posting
- `link` (string): Link to the job posting

### /delete_account

#### `DELETE`

- Allows users to delete their accounts.

#### Parameters

- `user_id` (string): ID of the user account to be deleted.

### /read_most_recent_jobs

#### `GET`

- Returns a specified number of most recent job postings or returns all jobs if there are fewer than the specified number.

#### Parameters

- `numbers` (string): Number of recent jobs to retrieve.

### /admin_delete_jobs

#### `DELETE`

- Allows admin accounts to delete a specific job based on its ID.

#### Parameters

- `admin_id` (string): ID of the admin performing the deletion.
- `job_id` (string): ID of the job to be deleted.

### /dev_delete_past_date

#### `DELETE`

- Allows a developer to delete all jobs past a certain date.

#### Parameters

- `invalid_past_date` (string): Date before which jobs should be deleted.

### /create_account

#### `PUT`

- Allows users to create a new account. 

#### Parameters

- `username` (string): Username for the new account.
- `email` (string): Email for the new account.
- `password` (string): Password for the new account.

### /login

#### `GET`

- Allows users to log in to their accounts.

#### Parameters

- `username` (string): Username for the login attempt.
- `password` (string): Password for the login attempt.

#### Response

- `status` (string): Success status.
- `message` (string): User ID of the logged-in user.

### /update_preferences

#### `PUT`

- Allows users to update their account preferences.

#### Parameters

- `user_id` (string): ID of the user account to be updated.
- `location` (string): Preferred location for job searches.
- `job_type` (string): Preferred job type for job searches.

### /get_preferences

#### `GET`

- Retrieves the account preferences for a user.

#### Parameters

- `user_id` (string): ID of the user account.

#### Response

- `preference` (object): User's account preferences.

### /add_new_job

#### `POST`

- Allows users to submit new job postings.

#### Parameters

- `company` (string): The company that posted the job
- `job_description` (string): Description of the job
- `job_type` (string): The type of job
- `location` (string): The location of the job
- `date` (string): The date of the posting
- `link` (string): Link to the job posting

### /delete_user_report

#### `DELETE`

- Allows deleting a user report based on its ID.

#### Parameters

- `report_id` (string): ID of the user report to be deleted.

### /get_job_by_id 

#### `GET`

- Allows users to get a job based on its ID. Returns the job that matches the ID.

#### Parameters

- `job_id` (string): ID of the job.

### /get_username_by_id

#### `GET`

- Allows users to get a username based on the user ID. Returns the username that matches the user ID.

#### Parameters

- `user_id` (string): ID of the user.   

### /search_jobs_by_vector

#### `GET`

- Allows users to search for jobs based on a search query. The search query is a string that is used to generate a vector using the OpenAI text-embedding-ada-002 model. The resulting vector is used to search for jobs that match the vector.

#### Parameters

- `query` (string): The search query.
- `limit` (int): The number of jobs to return.