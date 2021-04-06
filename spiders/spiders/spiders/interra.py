import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class InterraSpider(scrapy.Spider):
    name = "interra"
    allowed_domains = ["interra.tv"]
    start_urls = ["http://interra.tv/news/?page=1"]
    description = "новости в json формате"
    page = 1
    date_now = datetime.now().date()
    days = 7
    visited_urls = []
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        li = response.xpath("//ul[@class = 'news-list']/li").extract()
        for article in li:
            article = HtmlResponse(url="", body=article, encoding="utf-8")
            raw_date = article.xpath("//span/text()").extract()[0]
            title = article.xpath("//li/text()").extract()[0]
            publish_date = datetime.strptime(raw_date, "%d.%m.%Y")
            if (self.date_now - publish_date.date()).days <= self.days:
                yield {
                    "url": response.url,
                    "request_url": response.url,
                    "title": title,
                    "text": title,
                    "raw_date": raw_date,
                    "publish_date": self.tz.localize(publish_date),
                    "author": None,
                }
        last_date = datetime.strptime(
            HtmlResponse(url="", body=li[-1], encoding="utf-8")
            .xpath("//span/text()")
            .extract()[0],
            "%d.%m.%Y",
        ).date()
        if (self.date_now - last_date).days <= self.days:
            self.page += 1
            yield scrapy.Request(f"http://interra.tv/news/?page={self.page}")
