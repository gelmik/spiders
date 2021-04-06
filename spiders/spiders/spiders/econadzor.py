import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class EconadzorSpider(scrapy.Spider):
    name = "econadzor"
    allowed_domains = ["econadzor.com"]
    start_urls = ["http://econadzor.com/news"]
    page = 1
    description = "новости на одной странице"
    visited_urls = []
    days = 7
    tz = pytz.timezone("Europe/Moscow")
    date_now = datetime.now().date()
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

    def parse(self, response):
        divs = response.xpath("//div[@class = 'event']").extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_date = div.xpath("//p[@class = 'created']/text()").extract()[0].strip()
            publish_date = datetime(
                int(raw_date.split(" ")[2]),
                self.months[raw_date.split(" ")[1]],
                int(raw_date.split(" ")[0]),
            )
            if (self.date_now - publish_date.date()).days <= self.days:
                href = "http://econadzor.com" + div.xpath("//h2/a/@href").extract()[0]
                if href not in self.visited_urls:
                    yield scrapy.Request(
                        href,
                        callback=self.parse_article,
                        meta={"raw_date": raw_date, "publish_date": publish_date},
                    )
        last_raw_date = (
            HtmlResponse(url="", body=divs[-1], encoding="utf-8")
            .xpath("//p[@class = 'created']/text()")
            .extract()[0]
            .strip()
        )
        last_date = datetime(
            int(last_raw_date.split(" ")[2]),
            self.months[last_raw_date.split(" ")[1]],
            int(last_raw_date.split(" ")[0]),
        ).date()

        if (self.date_now - last_date).days <= self.days:
            self.page += 1
            yield scrapy.Request(f"http://econadzor.com/news?page={self.page}")

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath("//h1/text()").extract()[0],
            "text": " ".join(
                response.xpath(
                    "//div[@class= 'other-content container']/h1/following-sibling::*[position() < last()]//text()"
                ).extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
