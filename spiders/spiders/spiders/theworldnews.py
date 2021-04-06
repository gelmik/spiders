import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class TheworldnewsSpider(scrapy.Spider):
    name = "theworldnews"
    allowed_domains = ["theworldnews.net"]
    start_urls = ["https://theworldnews.net"]

    def parse(self, response):
        divs = json.loads(
            "".join(response.xpath("//div[@id = 'ru-today']/*").extract())
        )
        print("*" * 100, divs)
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            print(div.xpath("//h4/a/text()").extract()[0])
        last_data_timestamp = response.xpath(
            "//div[@id = 'ru-today']//div[@class = 'mb_content__item  '][last()]/@data-timestamp"
        ).extract()
        print(last_data_timestamp)
