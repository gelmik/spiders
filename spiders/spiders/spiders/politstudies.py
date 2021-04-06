import scrapy
from datetime import datetime
import pytz


class PolitstudiesSpider(scrapy.Spider):
    name = "www.politstudies.ru"
    allowed_domains = ["www.politstudies.ru"]
    start_urls = ["https://www.politstudies.ru/news.html?p=1"]
    page = 1
    description = "новости на одной странице"
    visited_urls = []
    days = 30
    tz = pytz.timezone("Europe/Moscow")

    def __init__(self, date_now=datetime.now().date()):
        self.date_now = date_now

    def parse(self, response):
        count = int(
            response.xpath("count(//b[@style = 'font-size:16px;']/text())")
            .extract()[0]
            .split(".")[0]
        )
        for index in range(1, count + 1):
            title = (
                response.xpath(f"//b[@style = 'font-size:16px;'][{index}]/text()")
                .extract()[0]
                .split(" г.")[1]
            )
            text = response.xpath(
                f"//b[@style = 'font-size:16px;'][{index}]/following-sibling::p[1]/text()"
            ).extract()[0]
            raw_date = (
                response.xpath(f"//b[@style = 'font-size:16px;'][{index}]/text()")
                .extract()[0]
                .split(" г")[0]
            )
            publish_date = datetime.strptime(raw_date, "%d.%m.%Y")
            if (self.date_now - publish_date.date()).days <= self.days:
                yield {
                    "url": response.url,
                    "request_url": response.url,
                    "title": title,
                    "text": text,
                    "raw_date": raw_date,
                    "publish_date": publish_date,
                    "author": None,
                }
        last_date = datetime.strptime(
            response.xpath(f"//b[@style = 'font-size:16px;'][{count}]/text()")
            .extract()[0]
            .split(" г")[0],
            "%d.%m.%Y",
        ).date()
        if (self.date_now - last_date).days <= self.days:
            self.page += 1
            yield scrapy.Request(f"https://www.politstudies.ru/news.html?p={self.page}")
