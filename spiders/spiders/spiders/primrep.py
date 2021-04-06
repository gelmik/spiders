import scrapy
from datetime import datetime, timedelta
from scrapy.http import HtmlResponse
import pytz


class PrimrepSpider(scrapy.Spider):
    name = "primrep"
    allowed_domains = ["primrep.ru"]
    start_urls = ["http://primrep.ru/"]
    next_page = True
    visited_urls = []
    days = 7
    date_now = datetime.now().date()
    tz = pytz.timezone("Europe/Moscow")

    def start_requests(self):
        yield scrapy.Request("http://primrep.ru", cookies={"beget": "begetok"})

    def parse(self, response):
        articles = response.xpath(
            "//article[contains(@class , 'entry-list clear')]"
        ).extract()
        for article in articles:
            article = HtmlResponse(url="", body=article, encoding="utf-8")
            href = article.xpath("//h2/a/@href").extract()[0]
            raw_date = (
                article.xpath("//time[@class = 'entry-date']/@datetime")
                .extract()[0]
                .split("+")[0]
            )
            publish_date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={"raw_date": raw_date, "publish_date": publish_date},
                )
        last_raw_date = (
            HtmlResponse(url="", body=articles[-1], encoding="utf-8")
            .xpath("//time[@class = 'entry-date']/@datetime")
            .extract()[0]
            .split("+")[0]
        )
        if (
            self.date_now - datetime.strptime(last_raw_date, "%Y-%m-%dT%H:%M:%S").date()
        ).days <= self.days:
            yield scrapy.Request(
                response.xpath("//a[@rel = 'next']/@href").extract()[0]
            )

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath("//h1/text()").extract()[0],
            "text": "\n".join(
                response.xpath("//div[@class = 'entry-content']/p//text()").extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
