import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class DvnovostiSpider(scrapy.Spider):
    name = "dvnovosti"
    allowed_domains = ["www.dvnovosti.ru"]
    start_urls = ["https://www.dvnovosti.ru/ajax/v1/content/"]
    page = 1
    description = "новости через api в json"
    visited_urls = []
    days = 7
    tz = pytz.timezone("Asia/Vladivostok")

    def __init__(self, date_now=datetime.now().date()):
        self.date_now = date_now

    def parse(self, response):
        hot = json.loads(response.body)["hot"]
        stories = json.loads(response.body)["stories"]
        for article in hot:
            raw_date = article["publishedAt"]
            publish_date = datetime.strptime(
                raw_date.split("+")[0], "%Y-%m-%dT%H:%M:%S"
            )
            if (self.date_now - publish_date.date()).days <= self.days:
                str_date = raw_date.split("T")[0].split("-")
                url = f"https://www.dvnovosti.ru/{article['categories'][0]['slug']}/{str_date[0]}/{str_date[1]}/{str_date[2]}/{article['id']}"
                href = f"https://www.dvnovosti.ru/ajax/v1/content/story/{article['categories'][0]['slug']}/{str_date[0]}/{str_date[1]}/{str_date[2]}/{article['id']}"
                if url not in self.visited_urls:
                    yield scrapy.Request(
                        href,
                        callback=self.parse_article,
                        meta={
                            "raw_date": raw_date,
                            "publish_date": publish_date,
                            "url": url,
                        },
                    )

        for article in stories:
            raw_date = article["publishedAt"]
            publish_date = datetime.strptime(
                raw_date.split("+")[0], "%Y-%m-%dT%H:%M:%S"
            )
            if (self.date_now - publish_date.date()).days <= self.days:
                str_date = raw_date.split("T")[0].split("-")
                url = f"https://www.dvnovosti.ru/{article['categories'][0]['slug']}/{str_date[0]}/{str_date[1]}/{str_date[2]}/{article['id']}"
                href = f"https://www.dvnovosti.ru/ajax/v1/content/story/{article['categories'][0]['slug']}/{str_date[0]}/{str_date[1]}/{str_date[2]}/{article['id']}"
                if url not in self.visited_urls:
                    yield scrapy.Request(
                        href,
                        callback=self.parse_article,
                        meta={
                            "raw_date": raw_date,
                            "publish_date": publish_date,
                            "url": url,
                        },
                    )

        last_date = datetime.strptime(
            stories[-1]["publishedAt"].split("+")[0], "%Y-%m-%dT%H:%M:%S"
        ).date()
        if (self.date_now - last_date).days <= self.days:
            yield scrapy.Request(
                f"https://www.dvnovosti.ru/ajax/v1/content/?last={stories[-1]['id']}",
                callback=self.next_stories,
            )

    def next_stories(self, response):
        stories = json.loads(response.body)["stories"]
        for article in stories:
            raw_date = article["publishedAt"]
            publish_date = datetime.strptime(
                raw_date.split("+")[0], "%Y-%m-%dT%H:%M:%S"
            )
            if (self.date_now - publish_date.date()).days <= self.days:
                str_date = raw_date.split("T")[0].split("-")
                url = f"https://www.dvnovosti.ru/{article['categories'][0]['slug']}/{str_date[0]}/{str_date[1]}/{str_date[2]}/{article['id']}"
                href = f"https://www.dvnovosti.ru/ajax/v1/content/story/{article['categories'][0]['slug']}/{str_date[0]}/{str_date[1]}/{str_date[2]}/{article['id']}"
                if url not in self.visited_urls:
                    yield scrapy.Request(
                        href,
                        callback=self.parse_article,
                        meta={
                            "raw_date": raw_date,
                            "publish_date": publish_date,
                            "url": url,
                        },
                    )

        last_date = datetime.strptime(
            stories[-1]["publishedAt"].split("+")[0], "%Y-%m-%dT%H:%M:%S"
        ).date()
        if (self.date_now - last_date).days <= self.days:
            yield scrapy.Request(
                f"https://www.dvnovosti.ru/ajax/v1/content/?last={stories[-1]['id']}",
                callback=self.next_stories,
            )

    def parse_article(self, response):
        data = json.loads(response.body)["story"]
        yield {
            "url": response.meta["url"],
            "request_url": response.url,
            "title": data["title"],
            "text": data["lead"]
            + "\n"
            + "\n".join(
                HtmlResponse(
                    url="", body=data["blocks"][0]["content"]["html"], encoding="utf-8"
                )
                .xpath("//text()")
                .extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
