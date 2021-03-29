import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse


class PolpredSpider(scrapy.Spider):
    name = "polpred"
    allowed_domains = ["polpred.com"]
    description = "новости на одной странице"
    start_urls = ["https://polpred.com/news/?ns=1&cat_a=on&page=1"]
    page = 1
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

    def start_requests(self):
        yield scrapy.Request(
            "https://polpred.com/news/?ns=1&cat_a=on&page=1",
            meta={"request_url": "https://polpred" ".com/news/?ns=1&cat_a=on&page=1"},
        )

    def parse(self, response):
        last_date = None
        articles = []
        for div in response.xpath("//div[@id='news_list']/div").extract():
            part = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_date = part.xpath(
                "//span[@class='news_breadcrumbs']/i[2]/text()"
            ).extract()[0]
            last_date = datetime(
                int(raw_date.split(" ")[2]),
                self.months[raw_date.split(" ")[1]],
                int(raw_date.split(" ")[0]),
            )
            articles.append(
                {
                    "url": response.url,
                    "request_url": response.meta["request_url"],
                    "title": " ".join(
                        part.xpath("//p[@class='newsn']//text()").extract()
                    ),
                    "text": "\n".join(
                        part.xpath("//p[position() > 1]//text()").extract()
                    ),
                    "raw_date": raw_date,
                    "publish_date": last_date,
                    "author": None,
                }
            )
            print(articles[-1]["title"], articles[-1]["raw_date"])
        for article in articles:
            yield article
        if (datetime.now() - last_date).days <= 7:
            self.page += 1
            url = f"https://polpred.com/news/?ns=1&cat_a=on&page={self.page}"
            yield scrapy.Request(url, meta={"request_url": url}, callback=self.parse)
