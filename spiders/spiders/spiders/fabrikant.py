import json
import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class FabrikantSpider(scrapy.Spider):
    name = "fabrikant"
    allowed_domains = ["www.fabrikant.ru"]
    page = 1
    start_urls = [
        "https://www.fabrikant.ru/main-pages/api/news/get-list/1/10?news_type=latest&date_from=undefined&date_to=undefined"
    ]
    visited_urls = []
    days = 7
    date_now = datetime.now().date()
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        items = json.loads(response.body)["result"]["newsList"]["items"]
        for item in items:
            raw_date = item["datePublication"]["date"].split(".")[0]
            publish_date = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            url = f"https://www.fabrikant.ru/news/v2/{item['newsId']}/view?news_type=latest"
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and url not in self.visited_urls:
                yield scrapy.Request(
                    f"https://www.fabrikant.ru/main-pages/api/news/{item['newsId']}",
                    callback=self.parse_article,
                    meta={
                        "raw_date": raw_date,
                        "publish_date": publish_date,
                        "url": url,
                    },
                )

        last_raw_date = items[-1]["datePublication"]["date"].split(".")[0]
        if (
            self.date_now - datetime.strptime(last_raw_date, "%Y-%m-%d %H:%M:%S").date()
        ).days <= self.days:
            self.page += 1
            yield scrapy.Request(
                f"https://www.fabrikant.ru/main-pages/api/news/get-list/{self.page}/10?news_type=latest&date_from=undefined&date_to=undefined"
            )

    def parse_article(self, response):
        data = json.loads(response.body)["result"]["item"][0]
        yield {
            "request_url": response.url,
            "url": response.meta["url"],
            "title": data["title"],
            "text": "\n".join(
                HtmlResponse(url="", body=data["content"], encoding="utf-8")
                .xpath("//text()")
                .extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
