import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class PvestiSpider(scrapy.Spider):
    name = "pvesti"
    allowed_domains = ["pvesti.ru", "www.pvesti.ru"]
    start_urls = [
        "http://pvesti.ru/2/arxiv-nomerov/&page=0",
        "http://www.pvesti.ru/2/v-nomere/&page=0",
    ]
    description = "новости в json формате"
    page = 1
    date_now = datetime.now().date()
    days = 7
    visited_urls = []
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        articles = response.xpath("//ul[@class = 'spisok-statei']/li").extract()
        for article in articles:
            article = HtmlResponse(url="", body=article, encoding="utf-8")
            raw_date = article.xpath("//span/text()").extract()[0]
            publish_date = datetime.strptime(raw_date, "%d.%m.%Y")
            if (self.date_now - publish_date.date()).days <= self.days:
                href = "http://pvesti.ru/" + article.xpath("//p/a/@href").extract()[0]
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={"raw_date": raw_date, "publish_date": publish_date},
                )
        last_raw_date = (
            HtmlResponse(url="", body=articles[-1], encoding="utf-8")
            .xpath("//span/text()")
            .extract()[0]
        )
        last_date = datetime.strptime(last_raw_date, "%d.%m.%Y").date()
        if (self.date_now - last_date).days <= self.days:
            href = (
                response.url.split("=")[0]
                + "="
                + str(int(response.url.split("=")[1]) + 1)
            )
            yield scrapy.Request(href)

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath("//div/h1//text()").extract()[0],
            "text": "\n".join(response.xpath("//article//div/p//text()").extract()),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
