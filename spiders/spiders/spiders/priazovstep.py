import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class PriazovstepSpider(scrapy.Spider):
    name = "priazovstep"
    allowed_domains = ["priazovstep.ru"]
    description = ""
    start_urls = ["https://priazovstep.ru/category/novosti/"]
    visited_urls = []
    days = 7
    date_now = datetime.now().date()
    tz = pytz.timezone("Europe/Moscow")
    months = {
        "января": 1,
        "февраля": 2,
        "марта": 3,
        "апреля": 4,
        "мая": 5,
        "июня": 6,
        "июля": 7,
        "августа": 8,
        "сентября": 9,
        "октября": 10,
        "ноября": 11,
        "декабря": 12,
    }

    def parse(self, response):
        divs = response.xpath("//div[@class= 'col-sm-6 col-lg-3 post-col']").extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            href = div.xpath("//div[@class = 'date']/a/@href").extract()[0]
            raw_date = div.xpath("//div[@class = 'date']/a/text()").extract()[0]
            publish_date = datetime(
                int(raw_date.split(" ")[2]),
                self.months[raw_date.split(" ")[1]],
                int(raw_date.split(" ")[0]),
                int(raw_date.split(" ")[3].split(":")[0]),
                int(raw_date.split(" ")[3].split(":")[1]),
            )
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={"raw_date": raw_date, "publish_date": publish_date},
                )
        last_raw_date = (
            HtmlResponse(url="", body=divs[-1], encoding="utf-8")
            .xpath("//div[@class = 'date']/a/text()")
            .extract()[0]
        )
        if (
            self.date_now
            - datetime(
                int(last_raw_date.split(" ")[2]),
                self.months[last_raw_date.split(" ")[1]],
                int(last_raw_date.split(" ")[0]),
            ).date()
        ).days <= self.days:
            yield scrapy.Request(
                response.xpath("//a[@class=  'next page-numbers']/@href").extract()[0]
            )

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath("//h1[@class = 'entry-title']/text()").extract()[0],
            "text": "\n".join(
                response.xpath(
                    "//main//div[@class = 'entry-content']/*//text()"
                ).extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
