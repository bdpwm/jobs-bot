import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import asyncio
from datetime import datetime



async def fetch_job_work_ua(job_name: str):
    print(f"Fetching jobs for: {job_name}")
    job_name = job_name.replace(" ", "+")

    ua = UserAgent()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'uk,en;q=0.9,ru;q=0.8',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': ua.random,
    }

    async with httpx.AsyncClient(follow_redirects=False) as client:
        response = await client.get(f'https://www.work.ua/jobs-{job_name}/', headers=headers)
        
        print(f"Response status code: {response.status_code}")

        if response.status_code == 301:
            print(f"Redirected to: {response.headers['Location']}")
            redirect_url = response.headers['Location']
            response = await client.get(redirect_url, headers=headers)
        
        if response.status_code != 200:
            print("Failed to fetch the job listings.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', class_='card-hover')

        if not job_cards:
            print("No job cards found.")
        
        for card in job_cards:
            title_tag = card.find('a', {'tabindex': '-1'})
            if not title_tag:
                continue

            job_href = title_tag.get('href')
            job_title = title_tag.get('title')

            if not job_title:  
                print("No title found for this job link.")
                continue

            salary_tag = card.find('div', class_='strong-600')
            salary = salary_tag.text.strip() if salary_tag else "Не вказано"

            company_tag = card.find('span', class_='strong-600')
            company = company_tag.text.strip() if company_tag else "Не вказано"


            job_id = job_href.split('/')[-1]
            job_href = title_tag.get('href')
