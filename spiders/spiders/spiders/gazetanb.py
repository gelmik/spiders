import scrapy
from datetime import datetime
import pytz
from scrapy.http import HtmlResponse

from ..spider import Spider


class GazetanbSpider(Spider):
    name = 'gazetanb.ru'
    allowed_domains = ['gazetanb.ru']
    start_urls = ['https://gazetanb.ru/cat/posts/']
    description = "дата только на странице списка новостей"
    visited_urls = []
    days = 7
    page = 1
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        articles = response.xpath(
            "//div[@class = 'jeg_posts jeg_load_more_flag']/article"
        ).extract()
        for article in articles:
            article = HtmlResponse(url="", body=article, encoding="utf-8")
            raw_date = article.xpath("//div[@class = 'jeg_meta_date']//a/text()").extract()[0]
            publish_date = datetime(
                int(raw_date.split(".")[2]),
                int(raw_date.split(".")[1]),
                int(raw_date.split(".")[0]),
            )
            if (self.date_now - publish_date.date()).days <= self.days:
                href = article.xpath("//h3/a/@href").extract()[0]
                if href not in self.visited_urls:
                    yield scrapy.Request(
                        href,
                        callback=self.parse_article,
                        meta={"raw_date": raw_date, "publish_date": publish_date},
                    )

        last_raw_date = (
            HtmlResponse(url="", body=articles[-1], encoding="utf-8")
                .xpath("//div[@class = 'jeg_meta_date']//a/text()")
                .extract()[0]
        )
        last_date = datetime(
            int(last_raw_date.split(".")[2]),
            int(last_raw_date.split(".")[1]),
            int(last_raw_date.split(".")[0]),
        ).date()
        if (self.date_now - last_date).days <= self.days:
            self.page += 1
            yield scrapy.Request(f"https://gazetanb.ru/cat/posts/page/{self.page}/")

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": self.clean_text(
                response.xpath("//h1/text()").extract()[0]
            ),
            "text": self.clean_text(
                " ".join(
                    response.xpath(
                        "//h2/text() | //div[contains(@class ,'content-inner')]/*//text()"
                    ).extract()
                )
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": self.tz.localize(response.meta["publish_date"]),
            "author": None,
        }
