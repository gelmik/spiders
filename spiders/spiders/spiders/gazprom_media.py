import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz
import re


class GazpromMediaSpider(scrapy.Spider):
    name = "gazprom-media.com"
    description = ""
    allowed_domains = ["gazprom-media.com"]
    start_urls = [
        "https://gazprom-media.com/api/news?filter%5Bwithout_multimedia%5D=1&page=1&per_page=6"  # noqa E501
    ]
    page_number = 1
    tz = pytz.timezone("Europe/Moscow")
    visited_urls = []

    def clean_text(self, text):
        text = text.replace("\xa0", " ")
        return re.sub(r"(\s){2,}", "\\1", text)

    def parse(self, response):
        articles = json.loads(response.body)["data"]
        for article in articles:
            href = "https://gazprom-media.com/api/news/" + article["slug"]
            if href not in self.visited_urls:
                article_date = article["date"].split("-")
                if (
                    datetime.now()
                    - datetime(
                        int(article_date[0]),
                        int(article_date[1]),
                        int(article_date[2]),  # noqa E501
                    )
                ).days <= 7:
                    yield scrapy.Request(
                        url=href,
                        meta={
                            "request_url": href,
                            "url": "https://gazprom-media.com/ru/media/"
                            + article["slug"],
                        },
                        callback=self.parse_article,
                    )
        last_date = articles[-1]["date"].split("-")
        if (
            datetime.now()
            - datetime(int(last_date[0]), int(last_date[1]), int(last_date[2]))
        ).days <= 7:
            self.page_number += 1
            yield scrapy.Request(
                f"https://gazprom-media.com/api/news?filter%5Bwithout_multimedia%5D=1&page={ self.page_number }&per_page=6"  # noqa E501
            )

    def parse_article(self, response):

        data = json.loads(response.body)["data"]
        raw_date = data["date"]
        title = data["name"]
        text = "\n".join(
            HtmlResponse(
                url="", body=data["sections"][0]["config"]["text_ru"], encoding="utf-8"
            )
            .xpath("//text()")
            .extract()
        )
        publish_date = datetime(
            int(raw_date.split("-")[0]),
            int(raw_date.split("-")[1]),
            int(raw_date.split("-")[2]),
            tzinfo=self.tz,
        )

        yield {
            "url": response.meta["url"],
            "request_url": response.meta["request_url"],
            "title": self.clean_text(title),
            "text": self.clean_text(text),
            "raw_date": raw_date,
            "publish_date": publish_date,
            "author": None,
        }
