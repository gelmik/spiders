import scrapy
from datetime import datetime, timedelta
from scrapy.http import HtmlResponse
import pytz


class PgrRuSpider(scrapy.Spider):
    name = "pgr.ru"
    description = "новости в корневом каталоге с пагинацией"
    allowed_domains = ["pgr.ru"]
    start_urls = ["https://pgr.ru/news"]
    page = 0
    date_now = datetime.now().date()
    days = 30
    visited_urls = []
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        divs = response.xpath(
            "//div[contains(@class , 'col-sm-4') and not(contains(@class , 'lg'))]"
        ).extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_article_date = div.xpath(
                "//span[contains(@class, 'date')]/text()"
            ).extract()[0]
            publish_article_date = datetime(
                int(raw_article_date.split(".")[2]),
                int(raw_article_date.split(".")[1]),
                int(raw_article_date.split(".")[0]),
            )

            href = response.urljoin(div.xpath("//h5/a/@href").extract()[0])
            if (
                self.date_now - publish_article_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield scrapy.Request(
                    url=href,
                    callback=self.parse_article,
                    meta={
                        "raw_date": raw_article_date,
                        "publish_date": publish_article_date,
                    },
                )

        last_raw_date = (
            HtmlResponse(url="", body=divs[-1], encoding="utf-8")
            .xpath("//span[contains(@class, 'date')]/text()")
            .extract()[0]
        )
        last_date = datetime(
            int(last_raw_date.split(".")[2]),
            int(last_raw_date.split(".")[1]),
            int(last_raw_date.split(".")[0]),
        ).date()
        if (self.date_now - last_date).days <= self.days:
            self.page += 1
            yield scrapy.Request(
                f"https://pgr.ru/news?page={self.page}", callback=self.parse
            )

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath("//h1/text()").extract()[0],
            "text": " ".join(
                response.xpath(
                    "//div[contains(@property, 'content:encoded')]//text()"
                ).extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
