import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse


class XnDtbegghdehagnwec3cgsXnP1aiSpider(scrapy.Spider):
    name = "xn----dtbegghdehagnwec3cgs.xn--p1ai"
    description = "новости на одной странице"
    allowed_domains = ["xn----dtbegghdehagnwec3cgs.xn--p1ai"]
    start_urls = ["http://моздокский-вестник.рф/news.html"]
    visited_urls = []
    days = 7
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
    now_date = datetime.now().date()

    def parse(self, response):
        for div in response.xpath("//div[@class='tmpl-item']").extract():
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            print(div.body)
            raw_article_date = (
                div.xpath("//div[@class='tmpl-date']/text()")
                .extract()[0]
                .replace(u"\xa0", " ")
            )
            print(raw_article_date.split(" "))
            publish_article_date = datetime(
                int(raw_article_date.split(" ")[2]),
                self.months[raw_article_date.split(" ")[1]],
                int(raw_article_date.split(" ")[0]),
            )
            if (self.now_date - publish_article_date.date()).days <= self.days:
                href = div.xpath("//a[@class='tmpl-title']/@href").extract()[0]
                yield scrapy.Request(
                    response.urljoin(href),
                    callback=self.parse_article,
                    meta={
                        "raw_date": raw_article_date,
                        "publish_date": publish_article_date,
                    },
                )

    def parse_article(self, response):

        yield {
            "request_url": response.url,
            "url": response.url,
            "title": response.xpath("//div[@class='maintitle']/text()").extract()[0],
            "text": " ".join(
                response.xpath(
                    "//div[contains(@class , 'clearfix')]/*[position() > 1]//text()"
                ).extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
