import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class QuadraSpider(scrapy.Spider):
    name = "quadra"
    allowed_domains = ["www.quadra.ru"]
    start_urls = ["https://www.quadra.ru/nk/"]
    description = ""
    page = 1
    date_now = datetime.now().date()
    days = 30
    visited_urls = []

    def parse(self, response):
        divs = response.xpath("//div[@class = 'post-content']").extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            href = response.urljoin(div.xpath("//h2/a/@href").extract()[0])
            raw_date = div.xpath("//time[@class = 'entry-date']/text()").extract()[0]
            publish_date = datetime(
                int(raw_date.split(".")[2]),
                int(raw_date.split(".")[1]),
                int(raw_date.split(".")[0]),
            )
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield scrapy.Request(
                    href,
                    meta={"raw_date": raw_date, "publish_date": publish_date},
                    callback=self.parse_article,
                )
        last_date = (
            HtmlResponse(url="", body=divs[-1], encoding="utf-8")
            .xpath("//time[@class = 'entry-date']/text()")
            .extract()[0]
        )
        if (
            self.date_now
            - datetime(
                int(last_date.split(".")[2]),
                int(last_date.split(".")[1]),
                int(last_date.split(".")[0]),
            ).date()
        ).days <= self.days:
            self.page += 1
            yield scrapy.Request(f"https://www.quadra.ru/nk/?PAGEN_1={self.page}")

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath("//h2/text()").extract()[0],
            "text": "\n".join(
                response.xpath(
                    "//div[@class = 'entry-content']/div[2]//text()"
                ).extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
