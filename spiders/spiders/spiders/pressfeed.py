import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class PressfeedSpider(scrapy.Spider):
    name = "pressfeed"
    description = "новости в json формате"
    allowed_domains = ["pressfeed.ru"]
    offset = 0
    limit = 25
    date_now = datetime.now().date()
    start_urls = ["https://api.pressfeed.ru/releases/view?offset=0&limit=25"]
    days = 7
    visited_urls = []
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        data = json.loads(response.body)["data"]
        for item in data:
            raw_date = item["created_at"]
            publish_date = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            href = f"https://pressfeed.ru/releases/{item['id']}"
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield {
                    "url": href,
                    "request_url": response.url,
                    "title": item["title"],
                    "text": item["lead"]
                    + "\n".join(
                        HtmlResponse(url="", body=item["text_html"], encoding="utf-8")
                        .xpath("//text()")
                        .extract()
                    ),
                    "raw_date": raw_date,
                    "publish_date": publish_date,
                    "author": None,
                }
        if (
            self.date_now
            - datetime.strptime(data[-1]["created_at"], "%Y-%m-%d %H:%M:%S").date()
        ).days <= self.days:
            self.offset += self.limit
            yield scrapy.Request(
                f"https://api.pressfeed.ru/releases/view?offset={self.offset}&limit={self.limit}"
            )
