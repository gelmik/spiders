import json
import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class Kazan24Spider(scrapy.Spider):
    name = "kazan24"
    description = ""
    allowed_domains = ["kazan24.ru"]
    start_urls = ["https://kazan24.ru/news"]
    visited_urls = []
    days = 7
    date_now = datetime.now().date()
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        divs = response.xpath(
            "//div[@class = 'c-news-item']//div[@class = 'c-news-item']"
        ).extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_date = div.xpath("//p/span[2]/text()").extract()[0]
            rtime, rdate = raw_date.split(", ")
            rtime = rtime.split(":")
            rdate = rdate.split(".")
            publish_date = datetime(
                int(rdate[2]),
                int(rdate[1]),
                int(rdate[0]),
                int(rtime[0]),
                int(rtime[1]),
            )
            href = div.xpath("//a[1]/@href").extract()[0]
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={
                        "request_url": href,
                        "raw_date": raw_date,
                        "publish_date": publish_date,
                    },
                )
        last_raw_date = (
            HtmlResponse(url="", body=divs[-1], encoding="utf-8")
            .xpath("//p/span[2]/text()")
            .extract()[0]
            .split(", ")[1]
            .split(".")
        )
        if (
            self.date_now
            - datetime(
                int(last_raw_date[2]), int(last_raw_date[1]), int(last_raw_date[0])
            )
        ).days <= self.days:
            yield scrapy.Request(
                response.xpath("//a[@class = 'next page-numbers']/@href").extract()[0]
            )

    def parse_article(self, response):
        yield {
            "request_url": response.meta["request_url"],
            "url": response.url,
            "title": response.xpath("//h1/text()").extract()[0],
            "text": "\n".join(
                response.xpath(
                    "//div[@class = 'c-content']/div[@class = 'c-news-item']/*[position() <= last() - 4]//text()"
                ).extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
