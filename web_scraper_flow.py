from prefect import flow, task
from typing import List, Dict
import logging
from basic_scrap import scrape_with_selenium

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@task(retries=3)
def scrape_website(url: str) -> Dict:
    logger.info(f"Scraping {url}")
    scrape_with_selenium(url)
    return {"url": url, "data": f"content from {url}"}


@flow
def main_flow(sites: Dict[str, List[str]] = None):
    if sites is None:
        sites = {
            "mvideo": ["https://www.mvideo.ru/product-list-page?q=samsung+galaxy"]
        }
    results = []
    for category, urls in sites.items():
        results.append(scrape_website.map(urls))
    return results


if __name__ == "__main__":
    main_flow.serve(
        name="scraping-development",
        cron="*/5 * * * *",
        parameters={
            "sites": {
                "mvideo": ["https://www.mvideo.ru/product-list-page?q=samsung+galaxy"]
            }
        },
        tags=["production"],
        description="Parallel web scraping every 5 mins",
    )
