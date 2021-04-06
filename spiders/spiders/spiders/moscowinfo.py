import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class MoscowinfoSpider(scrapy.Spider):
    name = "moscowinfo"
    description = "новости в корневом каталоге"
    allowed_domains = ["moscow-info.org"]
    start_urls = [
        "http://moscow-info.org/moskovskaya-zhizn.html",
        "http://moscow-info.org/obrazovanie.html",
        "http://moscow-info.org/mediczina.html",
        "http://moscow-info.org/sport.html",
        "http://moscow-info.org/moda.html",
        "http://moscow-info.org/pogoda.html",
        "http://moscow-info.org/ekonomika1.html",
        "http://moscow-info.org/ekonomika.html",
        "http://moscow-info.org/proishestviya.html",
        "http://moscow-info.org/zdes-interesno.html",
    ]
    visited_urls = []
    days = 30
    date_now = datetime.now().date()
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        divs = response.xpath("//div[@class = 'col-sm-12 col-md-6']").extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_date = (
                div.xpath("//span[@class = 'f1-s-3']/text()").extract()[0].strip()
            )
            href = "http://moscow-info.org/" + div.xpath("//h5/a/@href").extract()[0]
            publish_date = datetime(
                int(raw_date.split(" / ")[2]),
                int(raw_date.split(" / ")[1]),
                int(raw_date.split(" / ")[0]),
            )
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and href not in self.visited_urls:
                print(href)
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={"raw_date": raw_date, "publish_date": publish_date},
                )

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath(
                "//div[@class = 'col-md-10 col-lg-8 p-b-30']//h3/text()"
            ).extract()[0],
            "text": "\n".join(
                response.xpath(
                    "//div[@class = 'col-md-10 col-lg-8 p-b-30']//p/text()"
                ).extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
