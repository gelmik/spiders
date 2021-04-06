import scrapy
from datetime import datetime
import pytz
from scrapy.http import HtmlResponse

from ..spider import Spider


class ElgorskAdmSpider(Spider):
    name = "elgorsk-adm"
    allowed_domains = ["elgorsk-adm.ru"]
    start_urls = [
        "http://elgorsk-adm.ru/city-news?page=1",
        "http://elgorsk-adm.ru/region-news?page=1",
    ]
    page = 1
    description = "дата только на странице списка новостей"
    visited_urls = []
    days = 7
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        divs = response.xpath("//div[@class = 'nBlock']").extract()
        for div in divs:
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            raw_date = (
                div.xpath("//div[@class = 'newsArticleDate']/text()")
                .extract()[0]
                .strip()
            )
            publish_date = datetime.strptime(raw_date, "%d.%m.%Y %H:%M")
            if (self.date_now - publish_date.date()).days <= self.days:
                href = "http://elgorsk-adm.ru/" + div.xpath("//a/@href").extract()[0]
                if href not in self.visited_urls:
                    yield scrapy.Request(
                        href,
                        callback=self.parse_article,
                        meta={"raw_date": raw_date, "publish_date": publish_date},
                    )
        last_date = datetime.strptime(
            HtmlResponse(url="", body=divs[-1], encoding="utf-8")
            .xpath("//div[@class = 'newsArticleDate']/text()")
            .extract()[0]
            .strip(),
            "%d.%m.%Y %H:%M",
        ).date()

        if (self.date_now - last_date).days <= self.days:
            yield scrapy.Request(
                "http://elgorsk-adm.ru"
                + response.xpath("//a[@rel = 'next']/@href").extract()[0]
            )

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": self.clean_text(
                response.xpath("//h2[@class = 'newsView']/text()").extract()[0]
            ),
            "text": self.clean_text(
                "\n".join(
                    response.xpath(
                        "//div[@class = 'newsView chFont']//p/text()"
                    ).extract()
                )
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": self.tz.localize(response.meta["publish_date"]),
            "author": None,
        }
