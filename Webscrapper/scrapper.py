import requests
from bs4 import BeautifulSoup
import json

month_to_num = {"jan": '01', "feb": '02', "mar": '03', "apr": '04', "may": '05', "jun": '06', "jul": '07', "aug": '08', "sep": '09', "oct": '10', "nov": '11', "dec": '12'}
add_job_url = 'http://localhost:8000/add_new_job?company={}&job_description={}&job_type={}&location={}&date={}&link={}'
def scrap_job_table(url): 
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    div = soup.find('div', class_='Box-sc-g0xbh4-0 ehcSsh')

    jobs = div.find('table')
    for job in jobs.find_all('tr'):
        columns = job.find_all('td')
        if(len(columns) != 5): 
            continue
        company = columns[0].text
        job_title = columns[1].text
        location = columns[2].text
        link = str(columns[3].find('a')['href']).removesuffix('&utm_source=Simplify&ref=Simplify')
        date = columns[4].text
        month, day = date.split()
        date = f"{month} {day}"
        year = "2024"
        date_iso = f"{year}-{month_to_num[month.lower()]}-{day}"
        if(month == 'Dec'): 
            break
        res = requests.post(add_job_url.format(company, "", job_title,  location, date_iso, link))
        # break
    pass 

