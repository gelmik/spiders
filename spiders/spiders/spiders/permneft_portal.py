import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class PermneftPortalSpider(scrapy.Spider):
    name = "permneft_portal"
    allowed_domains = ["permneft-portal.ru"]
    start_urls = ["https://permneft-portal.ru/events/"]
    description = "новости через POST запрос"
    page = 1
    date_now = datetime.now().date()
    days = 7
    visited_urls = []
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        articles = response.xpath(
            "//article[contains(@class, 'main_article')]"
        ).extract()
        for article in articles:
            article = HtmlResponse(url="", body=article, encoding="utf-8")
            raw_date = article.xpath("//time/text()").extract()[0]
            publish_date = datetime.strptime(raw_date, "%d.%m.%Y")
            if (self.date_now - publish_date.date()).days <= self.days:
                yield {
                    "url": response.url,
                    "request_url": response.url,
                    "title": article.xpath("//strong/text()").extract()[0],
                    "text": "\n".join(
                        article.xpath(
                            "//div[@class= 'main_article-content']/p//text()"
                        ).extract()
                    ),
                    "raw_date": raw_date,
                    "publish_date": publish_date,
                    "author": None,
                }
        last_raw_date = (
            HtmlResponse(url="", body=articles[-1], encoding="utf-8")
            .xpath("//time/text()")
            .extract()[0]
        )
        last_date = datetime.strptime(last_raw_date, "%d.%m.%Y").date()
        if (self.date_now - last_date).days <= self.days:
            self.page += 1
            form_data = {"AJAX": "Y"}
            yield scrapy.FormRequest(
                f"https://permneft-portal.ru/events/?PAGEN_3={self.page}",
                formdata=form_data,
            )
