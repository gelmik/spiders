import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse


class AriOrgRuSpider(scrapy.Spider):
    name = "ari.org.ru"
    allowed_domains = ["ari.org.ru"]
    start_urls = ["http://ari.org.ru/"]
    visited_urls = []
    days = 7
    months = {
        "Янв": 1,
        "Фев": 2,
        "Мар": 3,
        "Апр": 4,
        "Май": 5,
        "Июн": 6,
        "Июл": 7,
        "Авг": 8,
        "Сен": 9,
        "Окт": 10,
        "Ноя": 11,
        "Дек": 12,
    }
    now_date = datetime.now().date()

    def parse(self, response):
        for div in response.xpath("//div[@id = 'main']/div[@class = 'post']").extract():
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_article_date = div.xpath("//span[@class='date']/text()").extract()[0]
            publish_article_date = datetime(
                int(raw_article_date.split(" ")[2]),
                self.months[raw_article_date.split(" ")[1]],
                int(raw_article_date.split(" ")[0]),
            )
            if (self.now_date - publish_article_date.date()).days <= self.days:
                yield scrapy.Request(
                    response.urljoin(
                        div.xpath("//a[@class = 'title']/@href").extract()[0]
                    ),
                    callback=self.parse_article,
                    meta={
                        "raw_date": raw_article_date,
                        "publish_date": publish_article_date,
                    },
                )
            else:
                break

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath("//div[@class = 'post']/h2/text()").extract()[0],
            "text": " ".join(
                response.xpath(
                    "//div[@class = 'post']/div[@class = 'content']/*[(self::h2 or self::p)][position() < last()]//text()"
                ).extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
