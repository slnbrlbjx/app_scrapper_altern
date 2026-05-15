from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

SEARCH_URL = (
    "https://fr.linkedin.com/jobs/search/"
    "?keywords=alternance%20cybers%C3%A9curit%C3%A9"
    "&location=Lille"
)


async def scrape_linkedin():
    jobs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.goto(SEARCH_URL)

        await page.wait_for_timeout(5000)

        html = await page.content()

        soup = BeautifulSoup(html, "html.parser")

        cards = soup.select(".base-search-card")

        for card in cards:
            title = card.select_one("h3")
            company = card.select_one("h4")
            link = card.select_one("a")

            jobs.append({
                "title": title.text.strip() if title else "",
                "company": company.text.strip() if company else "",
                "url": link["href"] if link else "",
                "source": "linkedin"
            })

        await browser.close()

    return jobs