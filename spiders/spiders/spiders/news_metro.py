from datetime import datetime

import pytz
import scrapy
from scrapy.http import HtmlResponse


class NewsMetroSpider(scrapy.Spider):
    name = "news.metro.ru"
    description = "новости на одной странице"
    allowed_domains = ["news.metro.ru"]
    start_urls = [
        "http://news.metro.ru/",
        f"http://news.metro.ru/mmnews{datetime.now().year}.html",
    ]
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
    tz = pytz.timezone("Europe/Moscow")

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={"request_url": url})

    def parse(self, response):
        in_article = False
        article = {
            "url": response.url,
            "request_url": response.meta["request_url"],
            "title": "",
            "text": "",
            "raw_date": "",
            "publish_date": None,
            "author": None,
        }
        for paragraph in response.xpath("//*[@align='left']/p").extract():
            if paragraph.find("strong") != -1 and in_article:
                if (datetime.now() - article["publish_date"]).days <= 7:
                    article["text"] = article["text"]
                    article["title"] = article["title"]
                    article["publish_date"] = self.tz.localize(article["publish_date"])
                    yield article
                article = {
                    "url": response.url,
                    "request_url": response.meta["request_url"],
                    "title": "",
                    "text": "",
                    "raw_date": "",
                    "publish_date": None,
                    "author": None,
                }
                part = HtmlResponse(url="", body=paragraph, encoding="utf-8")
                article["title"] = " ".join(
                    part.xpath("//p/text() | //p/*[not(self::strong)]/text()").extract()
                ).split(".")[0]
                article["raw_date"] = part.xpath("//strong/text()").extract()[0]
                article["publish_date"] = datetime(
                    int(article["raw_date"].split(" ")[2]),
                    self.months[article["raw_date"].split(" ")[1]],
                    int(article["raw_date"].split(" ")[0]),
                )
                article["text"] += "\n".join(
                    part.xpath("//p/text() | //p/*[not(self::strong)]/text()").extract()
                )
                continue
            if paragraph.find("strong") != -1 and not in_article:
                in_article = True
                part = HtmlResponse(url="", body=paragraph, encoding="utf-8")
                article["title"] = " ".join(
                    part.xpath("//p/text() | //p/*[not(self::strong)]/text()").extract()
                ).split(". ")[0]
                article["raw_date"] = part.xpath("//strong/text()").extract()[0]
                article["publish_date"] = datetime(
                    int(article["raw_date"].split(" ")[2]),
                    self.months[article["raw_date"].split(" ")[1]],
                    int(article["raw_date"].split(" ")[0]),
                )
                article["text"] += " ".join(
                    part.xpath("//p/text() | //p/*[not(self::strong)]/text()").extract()
                )
            article["text"] += " ".join(
                HtmlResponse(url="", body=paragraph, encoding="utf-8")
                .xpath("//text()")
                .extract()
            )
