import scrapy
from datetime import datetime
import pytz


class Pronso54Spider(scrapy.Spider):
    name = "pronso54.ru"
    description = "новости в корневом каталоге с пагинацией"
    allowed_domains = ["pronso54.ru"]
    start_urls = ["https://pronso54.ru/archive/"]
    next_page = True
    days = 7
    date_now = datetime.now().date()
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        for href in response.xpath("//h3[@class='teaser-title']/a/@href").extract():
            yield scrapy.Request(href, callback=self.parse_article)
        if self.next_page:
            yield scrapy.Request(
                response.xpath("//a[@class='next page-numbers']/@href").extract()[0]
            )

    def parse_article(self, response):
        raw_date = response.xpath(
            "//div[@id='post-content']/span[@style='font-size:10px;']/text()"
        ).extract()[0]
        publish_date = datetime(
            int(raw_date.split(".")[2]),
            int(raw_date.split(".")[1]),
            int(raw_date.split(".")[0]),
        )
        if (self.date_now - publish_date.date()).days <= self.days:
            yield {
                "url": response.url,
                "request_url": response.url,
                "title": response.xpath("//h1/text()").extract()[0],
                "text": "\n".join(
                    response.xpath("//div[@id= 'post-content']/p//text()").extract()
                ),
                "raw_date": raw_date,
                "publish_date": publish_date,
                "author": None,
            }
        else:
            self.next_page = False
