# Job Finder

Team members: Tanzir Hasan, Matthew Gong, Shao Jin, Michelle Lin

A job finder for adding/deleting and finding jobs of individual preferences. Serves as a personalized job finder where personal information and preferences are used. 

An example flask rest API server.

To build production, type `make prod`.

To create the env for a new developer, run `make dev_env`.


The following endpoints are present:

## What is this

This project defines a set of RESTful API endpoints for managing user accounts, job postings, and user reports related to job postings.

## EndPoints

### /endpoints

#### `GET`

- Returns a list of all available endpoints in the system.

### /UpdateUserInfo

#### `PUT`

- Allows updating a user's information. 

#### Parameters

- `_id` (string): User ID
- `changes` (object): Object containing changes to be made, including optional fields such as `email` and `username`.

### /add-user-report

#### `POST`

- Allows users to submit reports about job postings.

#### Parameters

- `user_id` (string): User ID submitting the report.
- `job_id` (string, optional): ID of the job being reported.
- `report` (string): The user's report.

### /get-user-reports

#### `GET`

- retrieve all user reports.

### /update-job-posting

#### `PUT`

- used to update job postings description.

#### Parameters

- `job_id` (string): ID of the job to be updated.
- `company` (string): The company that posted the job
- `job_title` (string): The job title of the posting
- `job_description` (string): description of the job
- `job_type` (string): the type of job
- `location` (string): the location of the job
- `date` (string): the date of the posting

### /delete-account

#### `DELETE`

- Allows users to delete their accounts.

#### Parameters

- `user_id` (string): ID of the user account to be deleted.

### /read_most_recent_jobs

#### `GET`

- Returns a specified number of most recent job postings or return all jobs if there is less than the specified number.

#### Parameters

- `numbers` (int): Number of recent jobs to retrieve.

### /admin_delete_jobs

#### `DELETE`

- Allows admin accounts to delete a specific job based on its ID.

#### Parameters

- `admin_id` (string): ID of the admin performing the deletion.
- `job_id` (string): ID of the job to be deleted.

### /admin_delete_past_date

#### `DELETE`

- Allows admin accounts to delete all jobs posted before a certain date.

#### Parameters

- `admin_id` (string): ID of the admin performing the deletion.
- `invalid_past_date` (string): Date before which jobs should be deleted.

### /create-account

#### `PUT`

- Allows users to create a new account. Takes username, email, and password. Fails if username or email matches one already in database.

#### Parameters

- `username` (string): Username for the new account.
- `email` (string): Email for the new account.
- `password` (string): Password for the new account.

### /update-preferences

#### `PUT`

- Allows users to update their account preferences. Account preferences include preferred location, preferred job type, and a sorting preference when conducting job searches.

#### Parameters

- `user_id` (string): ID of the user account to be updated.
- `location` (string): Preferred location for job searches.
- `job_type` (string): Preferred job type for job searches.
- `sort_by` (string): Sorting preference for job searches (e.g., Latest, Trending).

### /login-to-account

#### `PUT`

- Allows users to log in to their accounts. 

#### Parameters

- `user_id` (string): ID of the user attempting to log in.
- `password` (string): Password for the login attempt.

### /add-new-job

#### `POST`

- Allows users to submit new job postings. 

#### Parameters

- `company` (string): The company that posted the job
- `job_title` (string): The job title of the posting
- `job_description` (string): description of the job
- `job_type` (string): the type of job
- `location` (string): the location of the job
- `date` (string): the date of the posting

### /delete_user_report

#### `POST`

- Allows deleting a user report based on its ID.

#### Parameters

- `report_id` (string): ID of the user report to be deleted.

### /get_job_based_on_preference

#### `GET`

- Allows user to get jobs based on their user preferences. Returns jobs that matches their preferred location or preffered job type.

#### Parameters

- `user_id` (string): ID of the user.




