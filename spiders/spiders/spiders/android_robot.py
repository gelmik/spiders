import scrapy
from datetime import datetime
import pytz


class AndroidRobotSpider(scrapy.Spider):
    name = "android-robot"
    allowed_domains = ["android-robot.com"]
    start_urls = [
        "https://android-robot.com/category/novosti-hi-tech/",
        "https://android-robot.com/category/soft/",
        "https://android-robot.com/category/hardware/",
        "https://android-robot.com/category/internet/",
        "https://android-robot.com/category/nauka/",
    ]
    description = "новости в json формате"
    date_now = datetime.now().date()
    days = 7
    visited_urls = []
    categories = [
        {"category": "novosti-hi-tech", "page": 1, "nextpage": True},
        {"category": "soft", "page": 1, "nextpage": True},
        {"category": "hardware", "page": 1, "nextpage": True},
        {"category": "internet", "page": 1, "nextpage": True},
        {"category": "nauka", "page": 1, "nextpage": True},
    ]

    def is_next(self, meta):
        for category in self.categories:
            if category["category"] == meta["category"]:
                if category["nextpage"] == True:
                    category["page"] += 1
                return category["nextpage"]

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            yield scrapy.Request(url, meta=self.categories[i])

    def parse(self, response):
        for href in response.xpath("//h2[@class = 'entry-title']/a/@href").extract():
            yield scrapy.Request(href, callback=self.parse_article, meta=response.meta)
        if self.is_next(response.meta):
            yield scrapy.Request(
                response.xpath("//a[contains(@class , 'next')]/@href").extract()[0],
                meta=response.meta,
            )

    def parse_article(self, response):
        raw_date = (
            response.xpath("//time[@class = 'entry-date published']/@datetime")
            .extract()[0]
            .split("+")[0]
        )
        publish_date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
        if (self.date_now - publish_date.date()).days <= self.days:
            yield {
                "url": response.url,
                "request_url": response.url,
                "title": response.xpath(
                    "//h1[@class = 'entry-title']/text()"
                ).extract()[0],
                "text": "\n".join(
                    response.xpath("//div[@class = 'entry-content']/p/text()").extract()
                ),
                "raw_date": raw_date,
                "publish_date": publish_date,
                "author": None,
            }
        else:
            for category in self.categories:
                if category["category"] == response.meta["category"]:
                    category["nextpage"] = False
                    break
