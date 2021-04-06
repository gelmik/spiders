import scrapy
from datetime import datetime
import pytz
from scrapy.http import HtmlResponse

from ..spider import Spider


class GazetaStarSpider(Spider):
    name = 'gazeta-star.ru'
    allowed_domains = ['gazeta-star.ru']
    start_urls = ['https://gazeta-star.ru/?module=news&action=list&page=1']
    description = "дата только на странице списка новостей"
    visited_urls = []
    days = 7
    page = 1
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        divs = response.xpath(
            "//div[@class = 'central-content']//div[@class= 'item']"
        ).extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_date = div.xpath("//div[@class = 'date-time']/text()").extract()[0]
            publish_date = datetime(
                int(raw_date.split("-")[0]),
                int(raw_date.split("-")[1]),
                int(raw_date.split("-")[2]),
            )
            if (self.date_now - publish_date.date()).days <= self.days:
                href = (
                        "https://gazeta-star.ru"
                        + div.xpath("//a[@class= 'title']/@href").extract()[0]
                )
                if href not in self.visited_urls:
                    yield scrapy.Request(
                        href,
                        callback=self.parse_article,
                        meta={"raw_date": raw_date, "publish_date": publish_date},
                    )

        last_raw_date = (
            HtmlResponse(url="", body=divs[-1], encoding="utf-8")
                .xpath("//div[@class = 'date-time']/text()")
                .extract()[0]
        )
        last_date = datetime(
            int(last_raw_date.split("-")[0]),
            int(last_raw_date.split("-")[1]),
            int(last_raw_date.split("-")[2]),
        ).date()
        if (self.date_now - last_date).days <= self.days:
            self.page += 1
            yield scrapy.Request(f"https://gazeta-star.ru/?module=news&action=list&page={self.page}")

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": self.clean_text(
                response.xpath("//h1/text()").extract()[0]
            ),
            "text": self.clean_text(
                "\n".join(
                    response.xpath(
                        "//div[@class ='f-text']/*//text()"
                    ).extract()
                )
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": self.tz.localize(response.meta["publish_date"]),
            "author": None,
        }
