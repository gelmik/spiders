import scrapy
from datetime import datetime
import pytz

import re

from ..spider import Spider


class TpprkSpider(Spider):
    name = "tpprk.ru"
    allowed_domains = ["tpprk.ru"]
    start_urls = ["http://tpprk.ru"]
    page = 1
    description = "новости на одной странице"
    visited_urls = []
    days = 7
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        count = int(
            response.xpath("count(//div[@class = 'date_t']/text())")
            .extract()[0]
            .split(".")[0]
        )
        for index in range(1, count + 1):
            raw_date = self.clean_text(
                response.xpath(f"//div[@class = 'date_t'][{index}]/text()").extract()[0]
            )
            raw_date = (
                raw_date if raw_date.find("-") == -1 else raw_date.split("-")[1].strip()
            )
            publish_date = datetime(
                int(raw_date.split(" ")[2]),
                self.month_from_line_to_number(raw_date.split(" ")[1]),
                int(raw_date.split(" ")[0]),
            )
            if (self.date_now - publish_date.date()).days <= self.days:
                href = response.xpath(
                    f"//div[@class ='date_t'][{index}]/following-sibling::h3[1]/a[2]/@href"
                ).extract()
                if not href:
                    continue
                else:
                    href = "http://tpprk.ru" + href[0]
                if (
                    re.match(
                        r"http://tpprk\.ru/content/detail\.php\?articles=\d+", href
                    )
                    is not None
                ):
                    if href not in self.visited_urls:
                        yield scrapy.Request(
                            href,
                            callback=self.parse_article,
                            meta={"raw_date": raw_date, "publish_date": publish_date},
                        )

    def parse_article(self, response):
        yield {
            "url": response.url,
            "request_url": response.url,
            "title": response.xpath("//h4/text()").extract()[0],
            "text": "\n".join(
                response.xpath("//h4/following-sibling::p/text()").extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
