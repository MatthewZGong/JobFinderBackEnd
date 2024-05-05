# Job webscraper
This Python script scrapes a GitHub repository for job listings and stores them in a MongoDB database through our server API.


# Prerequisites
Before running the script, make sure you have the correct Python packages installed:

Its recomended to use a virtual environment to install the packages:

An example of how to install the packages using pip for a linux machine:

```
python -m venv venv
source venv/bin/activate
pip install -r req.txt 
```



# How to use
The script will scrape the job listings from the specified GitHub repository (https://github.com/SimplifyJobs/Summer2024-Internships) and send POST requests to the local server with the job details.

To run the script, you can use the following command:
```
python scrapper.py
```

This will scrape the job listings from the specified GitHub repository and send POST requests to the local server with the job details.
How it Works

The script imports the necessary libraries: requests for making HTTP requests, BeautifulSoup for parsing HTML.


The script is hardcoded to scrape job listings from the https://github.com/SimplifyJobs/Summer2024-Internships repository.

this script will also fail if github decides to change the structure of the website.

to scrape other websites, you will have to change the script because each website has a different structure.