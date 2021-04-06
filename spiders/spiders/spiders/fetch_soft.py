from datetime import datetime

import pytz
import scrapy
from scrapy.http import HtmlResponse


class KeepterSpider(scrapy.Spider):
    name = "fetch-soft.ru"
    description = "для более точного обхода можно использовать динамические ссылки"
    allowed_domains = ["fetch-soft.ru"]
    start_urls = ["http://fetch-soft.ru"]
    visited_urls = []
    days = 7
    date_now = datetime.now().date()
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        articles = response.xpath("//article").extract()
        for article in articles:
            article = HtmlResponse(url="", body=article, encoding="utf-8")
            raw_date = (
                article.xpath("//span[@class = 'posted-on']//time[1]/@datetime")
                .extract()[0]
                .split("+")[0]
            )
            publish_date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
            href = article.xpath("//h2/a/@href").extract()[0]
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield {
                    "url": href,
                    "request_url": response.url,
                    "title": article.xpath("//h2/a/text()").extract()[0],
                    "text": "\n".join(
                        article.xpath(
                            "//div[@class = 'entry-content']//*[not(self::noscript)]/text()"
                        ).extract()
                    ),
                    "raw_date": raw_date,
                    "publish_date": self.tz.localize(publish_date),
                    "author": None,
                }
        last_raw_date = (
            HtmlResponse(url="", body=articles[-1], encoding="utf-8")
            .xpath("//span[@class = 'posted-on']//time[1]/@datetime")
            .extract()[0]
            .split("+")[0]
        )
        last_date = datetime.strptime(last_raw_date, "%Y-%m-%dT%H:%M:%S").date()
        if (self.date_now - last_date).days <= self.days:
            yield scrapy.Request(
                response.xpath("//a[@class = 'next page-numbers']/@href").extract()[0]
            )
