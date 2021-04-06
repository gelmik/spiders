import scrapy
from datetime import datetime
import pytz
from scrapy.http import HtmlResponse

from ..spider import Spider


class TrkPutSpider(scrapy.Spider):
    name = "trk-put"
    allowed_domains = ["trk-put.ru"]
    start_urls = ["https://trk-put.ru/news", "https://trk-put.ru/analitika"]
    description = "дата только на странице списка новостей"
    visited_urls = []
    days = 7
    tz = pytz.timezone("Europe/Moscow")

    def start_requests(self):
        cookies = {
            "_smga": "GA1.2.1328854844.1617704321",
            "_smga_gid": "GA1.2.814845543.1617704321",
            "a8ad72bf448bb2161da117b40c60a438[3bc3610a11d31dda99e5178b92a58e0d]": "normal",
            "a8ad72bf448bb2161da117b40c60a438[logdate]": "1617704317",
            "a8ad72bf448bb2161da117b40c60a438[order_by]": "pubdate",
            "PHPSESSID": "6a171e44a8c9e6b0d0973f89c88d8a23",
        }
        for url in self.start_urls:
            yield scrapy.Request(
                url, meta={"page": 1}, cookies=cookies, callback=self.parse
            )

    def parse(self, response):
        print(response.body)
        divs = response.xpath("//div[@class= 'article_wrapper ltr']").extract()
        print(len(divs))
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_date = (
                div.xpath("//div[@class=  'date']/span/text()").extract()[0].strip()
            )
            print(raw_date.split(" "))
            publish_date = datetime.strptime(
                int(raw_date.split(" ")[2]),
                self.make_requests_from_url(raw_date.split(" ")[1]),
                int(raw_date.split(" ")[0]),
                int(raw_date.split(" ")[4].split(":")[0]),
                int(raw_date.split(" ")[4].split(":")[1]),
            )
            print(publish_date)
