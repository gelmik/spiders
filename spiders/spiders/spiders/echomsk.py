from datetime import datetime

import pytz
import scrapy


class EchomskSpider(scrapy.Spider):
    name = "echo.msk.ru"
    description = "Сайт с многоуровневой версткой (сбор программ)"
    allowed_domains = ["echo.msk.ru"]
    start_urls = ["https://echo.msk.ru/programs/"]
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
    tz = pytz.timezone("Europe/Moscow")
    visited_urls = []

    def parse(self, response):
        for href_program in response.xpath(
            '//div[@class="broadcast_list"]//h2/a/@href'
        ).extract():
            yield scrapy.Request(
                response.urljoin(href_program), callback=self.parse_page
            )

    def parse_page(self, response):
        for href in response.xpath(
            "//div[@class='rel']/div/div[@class='prevcontent']//a[contains(@class , 'read')]/@href"
        ).extract():
            href = response.urljoin(href)
            if href not in self.visited_urls:
                self.visited_urls.append(href)
                if len(self.visited_urls) <= 1000:

                    yield scrapy.Request(
                        response.urljoin(href),
                        callback=self.parse_article,
                        meta={"request_url": href},
                    )
        next_page = response.xpath("//a[@class='next']/@href").extract()
        if next_page and int(next_page[-1].split("/")[-2]) < 10:
            yield scrapy.Request(
                response.urljoin(next_page[-1]), callback=self.parse_page
            )

    def parse_article(self, response):
        raw_date = response.xpath(
            "//div[@class='title']/div[@class='date left']/strong/text()"
        ).extract()[0]
        publish_date = datetime(
            int(raw_date.split(" ")[2]),
            self.months[raw_date.split(" ")[1]],
            int(raw_date.split(" ")[0]),
        )
        if (datetime.now() - publish_date).days <= 30:
            yield {
                "url": response.url,
                "request_url": response.meta["request_url"],
                "title": "".join(
                    response.xpath(
                        "//div[@class='mmplayer']/div[@class='typical itemprop=']/p[2]/text()"
                    ).extract()
                ).strip(),
                "text": "".join(
                    response.xpath(
                        "//div[@class='mmplayer']/div[@class='typical itemprop=']/*//text()"
                    ).extract()
                ),
                "raw_date": raw_date,
                "publish_date": self.tz.localize(publish_date),
            }
