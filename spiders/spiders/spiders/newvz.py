import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class NewvzSpider(scrapy.Spider):
    name = "newvz"
    allowed_domains = ["newvz.ru"]
    start_urls = ["https://newvz.ru/info/category/economics"]

    def parse(self, response):
        body = HtmlResponse(
            url="", body=response.xpath("//body").extract()[0], encoding="utf-8"
        )
        print(body.body, body.xpath("//h2").extract())
