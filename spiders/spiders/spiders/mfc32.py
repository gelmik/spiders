import scrapy
from datetime import datetime


class Mfc32Spider(scrapy.Spider):
    name = "mfc32"
    allowed_domains = ["мфц32.рф", "xn--32-7lc6ak.xn--p1ai"]
    start_urls = ["http://мфц32.рф/news/"]

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

    def parse(self, response):
        for href, date in zip(
            response.xpath("//h3[@class = 'news-title']/a/@href").extract(),
            response.xpath("//div[@class = 'news-date']/text()").extract(),
        ):
            print(href)
            url = response.urljoin(href)
            print(url)
            yield scrapy.Request(url, callback=self.article_parse, meta={"date": date})
        next_page = response.xpath(
            "//div[@class = 'nav-pages']/a[last() - 1]/text()"
        ).get()
        if next_page == ">":
            yield scrapy.Request(
                response.urljoin(
                    response.xpath(
                        "//div[@class = 'nav-pages']/a[last() - 1]/@href"
                    ).get()
                ),
                callback=self.parse,
            )

    def article_parse(self, response):
        date = response.meta["date"].split(" ")
        yield {
            "url": response.url,
            "title": response.xpath("//h1/text()").get().strip(),
            "text": "".join(
                response.xpath(
                    "//div[@class = 'single-news-text']/text() | //div[@class = 'single-news-text']/div/text()"
                ).getall()
            ),
            "publish_date": datetime(int(date[2]), self.months[date[1]], int(date[0])),
            "raw_date": response.meta["date"],
        }
