import scrapy
from datetime import datetime
import pytz
from scrapy.http import HtmlResponse

from ..spider import Spider


class TyumPravdaSpider(Spider):
    name = "tyum-pravda.ru"
    allowed_domains = ["tyum-pravda.ru"]
    start_urls = ["http://tyum-pravda.ru/news"]
    description = "дата только на странице списка новостей"
    visited_urls = []
    days = 7
    offset = 0
    count = 15
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        divs = response.xpath(
            "//div[@class= 'left-column']//div[@class ='item']"
        ).extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_date = div.xpath("//div[@class = 'date']/text()").extract()[0]
            publish_date = datetime(
                int(raw_date.split(" ")[2]),
                self.month_from_line_to_number(raw_date.split(" ")[1]),
                int(raw_date.split(" ")[0]),
            )
            if (self.date_now - publish_date.date()).days <= self.days:
                href = (
                    "http://tyum-pravda.ru"
                    + div.xpath("//div[@class = 'title']/a/@href").extract()[0]
                )
                if href not in self.visited_urls:
                    yield scrapy.Request(
                        href,
                        callback=self.parse_article,
                        meta={"raw_date": raw_date, "publish_date": publish_date},
                    )

        last_raw_date = (
            HtmlResponse(url="", body=divs[-1], encoding="utf-8")
            .xpath("//div[@class = 'date']/text()")
            .extract()[0]
        )
        last_date = datetime(
            int(last_raw_date.split(" ")[2]),
            self.month_from_line_to_number(last_raw_date.split(" ")[1]),
            int(last_raw_date.split(" ")[0]),
        ).date()
        if (self.date_now - last_date).days <= self.days:
            self.offset += self.count
            yield scrapy.Request(f"http://tyum-pravda.ru/news?start={self.offset}")

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": self.clean_text(
                response.xpath("//div[@class= 'left-column']/h1/text()").extract()[0]
            ),
            "text": self.clean_text(
                "\n".join(
                    response.xpath(
                        "//div[contains(@class, 'article-body')]/*//text()"
                    ).extract()
                )
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": self.tz.localize(response.meta["publish_date"]),
            "author": None,
        }
