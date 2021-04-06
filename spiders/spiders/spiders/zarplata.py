import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class ZarplataSpider(scrapy.Spider):
    name = "www.zarplata.ru"
    allowed_domains = ["www.zarplata.ru"]
    start_urls = [
        "https://api.content.zp.ru/v1/contents?offset=0&geo_id=1177&limit=25&type=news"
    ]
    description = "новости в json формате"
    offset = 0
    limit = 25
    date_now = datetime.now().date()
    days = 1000
    visited_urls = []

    def parse(self, response):
        articles = json.loads(response.body)["articles"]
        for article in articles:
            raw_date = article["created_at"].split("+")[0]
            publish_date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
            href = f"https://www.zarplata.ru{article['url']}"
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield {
                    "url": href,
                    "request_url": response.url,
                    "title": article["header"],
                    "text": "\n".join(
                        HtmlResponse(
                            url="", body=article["text_html"], encoding="utf-8"
                        )
                        .xpath("//text()")
                        .extract()
                    ),
                    "raw_date": raw_date,
                    "publish_date": pytz.utc.localize(publish_date),
                    "author": None,
                }
        if (
            self.date_now
            - datetime.strptime(
                articles[-1]["created_at"].split("+")[0], "%Y-%m-%dT%H:%M:%S"
            ).date()
        ).days <= self.days:
            self.offset += self.limit
            yield scrapy.Request(
                f"https://api.content.zp.ru/v1/contents?offset={self.offset}&limit={self.limit}&type=news"
            )
