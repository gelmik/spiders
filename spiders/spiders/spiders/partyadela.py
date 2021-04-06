import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class PartyadelaSpider(scrapy.Spider):
    name = "partyadela.ru"
    description = "страницы получаются через POST запрос"
    allowed_domains = ["partyadela.ru"]
    start_urls = ["https://partyadela.ru/news/?PAGEN_3=1"]
    page = 1
    visited_urls = []
    days = 7
    date_now = datetime.now().date()
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        divs = response.xpath(
            "//div[contains(@class , 'col-xs-12') and contains(@id, 'bx_')]"
        ).extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_date = (
                div.xpath("//div[@class = 'item__date']/text()").extract()[0].strip()
            )
            publish_date = datetime.strptime(raw_date, "%d.%m.%Y")
            href = "https://partyadela.ru" + div.xpath("//a/@href").extract()[0]
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={"raw_date": raw_date, "publish_date": publish_date},
                )
            print(publish_date)
        last_raw_date = (
            HtmlResponse(url="", body=divs[-1], encoding="utf-8")
            .xpath("//div[@class = 'item__date']/text()")
            .extract()[0]
            .strip()
        )
        last_date = datetime.strptime(last_raw_date, "%d.%m.%Y").date()
        if (self.date_now - last_date).days <= self.days:
            self.page += 1
            form_data = {"is_ajax": "y", "update": "n"}
            yield scrapy.FormRequest(
                f"https://partyadela.ru/news/?&PAGEN_3={self.page}", formdata=form_data
            )

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath("//h1/text()").extract()[0],
            "text": "".join(
                response.xpath(
                    "//article/div[@class = 'page-header']/h2/text() | //article/p//text()"
                ).extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
