import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse


class WwwNkOnlineRuSpider(scrapy.Spider):
    name = "www.nk-online.ru"
    description = "новости на одной странице"
    allowed_domains = ["www.nk-online.ru"]
    start_urls = ["http://www.nk-online.ru/news/"]
    date_now = datetime.now().date()
    days = 7
    visited_urls = []
    months = {
        "Января": 1,
        "Февраля": 2,
        "Марта": 3,
        "Апреля": 4,
        "Мая": 5,
        "Июня": 6,
        "Июля": 7,
        "Августа": 8,
        "Сентября": 9,
        "Октября": 10,
        "Ноября": 11,
        "Декабря": 12,
    }
    page = 1
    id_request = ""

    def parse(self, response):
        divs = response.xpath("//div[@class='news-item']").extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_article_date = div.xpath("//div[@class = 'date']/text()").extract()[0]
            publish_article_date = datetime(
                2021,
                self.months[raw_article_date.split(" ")[1]],
                int(raw_article_date.split(" ")[0]),
                int(raw_article_date.split(" ")[3].split(":")[0]),
                int(raw_article_date.split(" ")[3].split(":")[1]),
            )
            href = response.urljoin(div.xpath("//h3/a/@href").extract()[0])
            if (
                self.date_now - publish_article_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={
                        "raw_date": raw_article_date,
                        "publish_date": publish_article_date,
                    },
                )
        last_raw_date = (
            HtmlResponse(url="", body=divs[-1], encoding="utf-8")
            .xpath("//div[@class = 'date']/text()")
            .extract()[0]
        )
        last_date = datetime(
            2021,
            self.months[last_raw_date.split(" ")[1]],
            int(last_raw_date.split(" ")[0]),
        )
        if (self.date_now - last_date.date()).days <= self.days:
            self.page += 1
            self.id_request = (
                response.xpath("//div[@class='col-md-9']/div[1]/@id")
                .extract()[0]
                .split("_")[1]
            )
            href = f"http://www.nk-online.ru/news/?bxajaxid={self.id_request}&PAGEN_2={self.page}"
            yield scrapy.Request(href, callback=self.next_articles)

    def next_articles(self, response):
        divs = response.xpath("//div[@class='news-item']").extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_article_date = div.xpath("//div[@class = 'date']/text()").extract()[0]
            publish_article_date = datetime(
                2021,
                self.months[raw_article_date.split(" ")[1]],
                int(raw_article_date.split(" ")[0]),
                int(raw_article_date.split(" ")[3].split(":")[0]),
                int(raw_article_date.split(" ")[3].split(":")[1]),
            )
            href = response.urljoin(div.xpath("//h3/a/@href").extract()[0])
            if (
                self.date_now - publish_article_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={
                        "raw_date": raw_article_date,
                        "publish_date": publish_article_date,
                    },
                )
        last_raw_date = (
            HtmlResponse(url="", body=divs[-1], encoding="utf-8")
            .xpath("//div[@class = 'date']/text()")
            .extract()[0]
        )
        last_date = datetime(
            2021,
            self.months[last_raw_date.split(" ")[1]],
            int(last_raw_date.split(" ")[0]),
        )
        if (self.date_now - last_date.date()).days <= self.days:
            self.page += 1
            href = f"http://www.nk-online.ru/news/?bxajaxid={self.id_request}&PAGEN_2={self.page}"
            yield scrapy.Request(href, callback=self.next_articles)

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath("//h2/text()").extract()[0],
            "text": " ".join(
                response.xpath("//div[@class = 'detail-text']//text()").extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
