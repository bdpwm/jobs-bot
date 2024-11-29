import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import asyncio
from datetime import datetime
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
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', class_='card-hover')
        if not job_cards:
            return

        for card in job_cards:
            title_tag = card.find('a', {'tabindex': '-1'})
            if not title_tag:
                continue

            job_data = {
                "title": title_tag.get('title'),
                "job_from": "work.ua",
                "salary": card.find('div', class_='strong-600').text.strip() if card.find('div', class_='strong-600') else "Не вказано",
                "company": card.find('span', class_='strong-600').text.strip() if card.find('span', class_='strong-600') else "Не вказано",
                "location": "Не вказано",
                "link": title_tag.get('href')
            }

            await save_job(job_data, user_id)