import scrapy
from datetime import datetime
import pytz
from scrapy.http import HtmlResponse

from ..spider import Spider


class MoykurskSpider(Spider):
    name = 'moykursk'
    allowed_domains = ['moykursk.ru']
    start_urls = ['https://moykursk.ru/arhive-news']
    description = "дата только на странице списка новостей"
    visited_urls = []
    days = 7
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        divs = response.xpath(
            "//div[@itemprop = 'articleBody']//div[@class ='jn']"
        ).extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_date = div.xpath("//span[@class ='jn-small']/text()").extract()[0]
            publish_date = datetime(
                int(raw_date.split(".")[2]),
                int(raw_date.split(".")[1]),
                int(raw_date.split(".")[0]),
            )
            if (self.date_now - publish_date.date()).days <= self.days:
                href = (
                        "https://moykursk.ru"
                        + div.xpath("//h4/a/@href").extract()[0]
                )
                if href not in self.visited_urls:
                    yield scrapy.Request(
                        href,
                        callback=self.parse_article,
                        meta={"raw_date": raw_date, "publish_date": publish_date},
                    )


    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": self.clean_text(
                response.xpath("//h2[@itemprop = 'name']/text()").extract()[0]
            ),
            "text": self.clean_text(
                "\n".join(
                    response.xpath(
                        "//div[@itemprop = 'articleBody']/p[position() < last()]//text()"
                    ).extract()
                )
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": self.tz.localize(response.meta["publish_date"]),
            "author": None,
        }
