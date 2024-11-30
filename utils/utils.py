import asyncio
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from db_handlers.db import save_job


async def fetch_job_work_ua(job_name: str, user_id: int):
    print(f"Fetching jobs for: {job_name}")
    job_name = job_name.replace(" ", "+")

    ua = UserAgent()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'uk,en;q=0.9,ru;q=0.8',
        'user-agent': ua.random,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(f'https://www.work.ua/jobs-{job_name}/', headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch data, status code: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', class_='card-hover')
        if not job_cards:
            return

        for card in job_cards:
            title_tag = card.find('a', {'tabindex': '-1'})
            if not title_tag:
                continue

            title = title_tag.get('title', "Not specified").strip()

            salary = "Not specified"
            salary_tag = card.find('span', class_='strong-600')
            if salary_tag and "грн" in salary_tag.text:
                salary = salary_tag.text.strip()

            company_tag = card.find('div', class_='mt-xs')
            company_name_tag = company_tag.find('span', class_='strong-600')
            company_name = company_name_tag.get_text(strip=True)

            city_tags = company_tag.find_all('span', class_='')
            distance = ""

            for tag in city_tags:
                tag_text = tag.get_text(strip=True)
                if tag_text and tag_text not in ['']:
                    distance_block = tag.find_parent('span', class_='distance-block')
                    if not distance_block:
                        location = tag_text
                    else:
                        distance = tag_text
                        break 

            company = f"{company_name}, {location}"
            if distance:
                company += f" {distance}"

            link = title_tag.get('href', "Not specified").strip()

            job_data = {
                "title": title,
                "job_from": "work.ua",
                "salary": salary,
                "company": company,
                "link": link,
            }

            await save_job(job_data, user_id)