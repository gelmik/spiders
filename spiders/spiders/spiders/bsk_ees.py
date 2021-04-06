import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class BskEesSpider(scrapy.Spider):
    name = "bsk_ees"
    description = "новости со скрытым текстом на одной странице"
    allowed_domains = ["bsk-ees.ru"]
    start_urls = [
        "https://bsk-ees.ru/novosti?year=2021",
        "https://bsk-ees.ru/novosti?year=2022",
        "https://bsk-ees.ru/novosti?year=2023",
        "https://bsk-ees.ru/novosti?year=2024",
    ]
    visited_urls = []
    days = 30
    date_now = datetime.now().date()
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        divs = response.xpath("//div[@class= 'mt-4']").extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_date = (
                div.xpath("//b[@class= 'text_preview_date']/text()")
                .extract()[0]
                .strip()
            )
            publish_date = datetime(
                int(response.url.split("=")[1]),
                int(raw_date.split(".")[1]),
                int(raw_date.split(".")[0]),
            )
            if (self.date_now - publish_date.date()).days <= self.days:
                yield {
                    "url": response.url,
                    "request_url": response.url,
                    "title": div.xpath("//div[@class= 'bold-title']/span/text()")
                    .extract()[0]
                    .strip(),
                    "text": "\n".join(
                        div.xpath(
                            "//div[@class = 'text-wrap']//div[@class = 'text' ]//text()"
                        ).extract()
                    ),
                    "raw_date": raw_date,
                    "publish_date": publish_date,
                    "author": None,
                }
