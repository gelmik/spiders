import scrapy
import dateparser
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class VrtSpider(scrapy.Spider):
    name = "vrt"
    allowed_domains = ["vrt.tv"]
    start_urls = ["http://vrt.tv/news/"]
    description = "новости в json формате"
    page = 1
    date_now = datetime.now().date()
    days = 7
    visited_urls = []
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        articles = response.xpath("//ul[@class = 'services__list']/li").extract()
        for artcile in articles:
            artcile = HtmlResponse(url="", body=artcile, encoding="utf-8")
            raw_date = artcile.xpath(
                "//div[@class = 'services__inf-time']/text()"
            ).extract()[0]
            str_date = str(dateparser.parse(raw_date, languages=["ru"]))
            publish_date = (
                datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S")
                if str_date.find(".") == -1
                else datetime.strptime(str_date.split(".")[0], "%Y-%m-%d %H:%M:%S")
            )
            if (self.date_now - publish_date.date()).days <= self.days:
                href = (
                    "http://vrt.tv/"
                    + artcile.xpath(
                        "//div[@class = 'services__title']/a/@href"
                    ).extract()[0]
                )
                if href not in self.visited_urls:
                    yield scrapy.Request(
                        href,
                        callback=self.parse_article,
                        meta={"raw_date": raw_date, "publish_date": publish_date},
                    )
        last_raw_date = (
            HtmlResponse(url="", body=articles[-1], encoding="utf-8")
            .xpath("//div[@class = 'services__inf-time']/text()")
            .extract()[0]
        )
        last_str_date = str(dateparser.parse(last_raw_date, languages=["ru"]))
        last_date = (
            datetime.strptime(last_str_date, "%Y-%m-%d %H:%M:%S").date()
            if last_str_date.find(".") == -1
            else datetime.strptime(
                last_str_date.split(".")[0], "%Y-%m-%d %H:%M:%S"
            ).date()
        )
        if (self.date_now - last_date).days <= self.days:
            self.page += 1
            yield scrapy.Request(f"http://vrt.tv/news/?page={self.page}")

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath("//main//h1/text()").extract()[0],
            "text": " ".join(
                response.xpath(
                    "//div[@class = 'box-content box-content-left']/p//text()"
                ).extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
