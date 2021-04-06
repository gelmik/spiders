import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class OskoladminSpider(scrapy.Spider):
    name = "oskoladmin"
    allowed_domains = ["oskoladmin.ru"]
    description = "новости в json формате"
    offset = 0
    limit = 24
    date_now = datetime.now().date()
    start_urls = [
        "https://oskoladmin.ru/press-centr/?order=creation_date_desc&offset=0&limit=24&format=json"
    ]
    days = 7
    visited_urls = []
    tz = pytz.timezone("Europe/Moscow")
    months = {
        "Янв": 1,
        "Фев": 2,
        "Мар": 3,
        "Апр": 4,
        "Май": 5,
        "Июн": 6,
        "Июл": 7,
        "Авг": 8,
        "Сен": 9,
        "Окт": 10,
        "Ноя": 11,
        "Дек": 12,
    }

    def parse(self, response):
        data = json.loads(response.body)["initialEntities"]
        for item in data:
            raw_date = item["creation_date"]
            publish_date = datetime(
                int(raw_date.split(" ")[2]),
                self.months[raw_date.split(" ")[1]],
                int(raw_date.split(" ")[0]),
                int(raw_date.split(" ")[3].split(":")[0]),
                int(raw_date.split(" ")[3].split(":")[1]),
            )
            href = f"https://oskoladmin.ru/press-centr/{item['slug']}"
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={"raw_date": raw_date, "publish_date": publish_date},
                )
        if (
            self.date_now
            - datetime(
                int(data[-1]["creation_date"].split(" ")[2]),
                self.months[data[-1]["creation_date"].split(" ")[1]],
                int(data[-1]["creation_date"].split(" ")[0]),
            )
        ).days <= self.days:
            self.offset += self.limit
            yield scrapy.Request(
                f"https://oskoladmin.ru/press-centr/?order=creation_date_desc&offset={self.offset}&limit={self.limit}&format=json"
            )

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath("//header/h1/text()").extract()[0],
            "text": "\n".join(
                response.xpath("//section//div[@class = 'col']/p//text()").extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
