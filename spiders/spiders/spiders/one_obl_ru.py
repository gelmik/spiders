import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class OneOblRuSpider(scrapy.Spider):
    name = "one_obl_ru"
    allowed_domains = ["www.1obl.ru"]
    start_urls = ["http://www.1obl.ru/"]
    cookies = {}
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36 OPR/74.0.3911.218 (Edition Yx 05)",
    }

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.get_cookies)

    def get_cookies(self, response):
        cookies = (
            response.headers.getlist("Set-Cookie")[0]
            .decode("utf-8")
            .split(";")[0]
            .split("=")
        )
        for cookie in cookies:
            print(cookie)
            self.cookies[cookie.split("=")[0]] = cookie.split("=")[1]
        yield scrapy.Request(
            self.start_urls[0],
            cookies=self.cookies,
            headers=self.headers,
            callback=self.parse,
        )

    def parse(self, response):
        print()
        print(response.body)
        for href in response.xpath(
            "//div[@class='col-12 col-md-6 col-xl-4 mb-4']/a/@href"
        ).extract():

            print(href)
