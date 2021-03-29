import scrapy
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class RadiovestiRuSpider(scrapy.Spider):
    name = "radiovesti.ru"
    description = "Парсер собирает с сайта программы Вести ФМ"
    allowed_domains = ["radiovesti.ru"]
    start_urls = ["http://radiovesti.ru/brand/"]
    tz = pytz.timezone("Europe/Moscow")
    visited_urls = []
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
        for programm_href in response.xpath(
            "//ul[@class='programms-list']/li[@class = 'programms-list__item']/a/@href"
        ).extract():
            yield scrapy.Request(
                url=f"http://radiovesti.ru{programm_href}",
                callback=self.parse_programm_page,
            )
        print(
            response.xpath(
                "//ul[@class='pager']/li[@class='pager__item'][last()]/a/text()"
            ).extract()[0]
        )
        last_page = int(
            response.xpath(
                "//ul[@class='pager']/li[@class='pager__item'][last()]/a/text()"
            ).extract()[0]
        )
        page = (
            int(
                response.xpath(
                    "count(//ul[@class='pager']/li/a[@class = 'pager__link pager__link_active']/../preceding-sibling::li)"  # noqa E501
                )
                .extract()[0]
                .split(".")[0]
            )
            + 1
        )
        if page + 1 <= last_page:
            yield scrapy.Request(f"http://radiovesti.ru/brand/page/{page + 1}/")

    def parse_programm_page(self, response):
        next_page = True
        for div in response.xpath(
            "//div[contains(@class , 'programms-page__list-wrap')]/div[contains(@class , 'news') and not(contains(@class , 'banner'))]"  # noqa E501
        ).extract():
            div = HtmlResponse(url="", body=div, encoding="utf-8")
            article_raw_date = (
                div.xpath("//div[@class='news__date']/text()")
                .extract()[0]
                .split(",")[0]
                .split(".")
            )
            article_date = datetime(
                int(article_raw_date[2]),
                int(article_raw_date[1]),
                int(article_raw_date[0]),
            )
            if (datetime.now() - article_date).days <= 7:
                href = (
                    "http://radiovesti.ru"
                    + div.xpath("//div[@class='news__content']/h1/a/@href").extract()[0]
                )
                if href not in self.visited_urls:
                    yield scrapy.Request(
                        href, callback=self.parse_article, meta={"request_url": href}
                    )
            else:
                next_page = False
                break
        if next_page:
            last_page = int(
                response.xpath(
                    "//ul[@class='pager']/li[@class='pager__item'][last()]/a/text()"
                ).extract()[0]
            )
            page = (
                int(
                    response.xpath(
                        "count(//ul[@class='pager']/li/a[@class = 'pager__link pager__link_active']/../preceding-sibling::li)"  # noqa E501
                    )
                    .extract()[0]
                    .split(".")[0]
                )
                + 1
            )
            if page + 1 <= last_page:
                yield scrapy.Request(
                    response.urljoin(f"page/{page + 1}"),
                    callback=self.parse_programm_page,
                )

    def parse_article(self, response):
        raw_date = response.xpath(
            "//div[@class = 'news__content']//div[@class='news__date']/text()"
        ).extract()[0]
        publish_date = self.create_date(raw_date)
        title = response.xpath(
            "//div[@class = 'news__content']//h1[@class = 'h1-title']/text()"
        ).extract()[0]
        text = " ".join(
            response.xpath(
                "//div[@class = 'insides-page clearfix']//div[contains(@class , 'insides-page__news__text')]//text()"  # noqa E501
            ).extract()
        )
        yield {
            "url": response.url,
            "request_url": response.meta["request_url"],
            "title": title,
            "raw_date": raw_date,
            "publish_date": publish_date,
            "text": text,
            "author": None,
        }

    def create_date(self, raw_date):
        _time, _date = raw_date.split(", ")
        _time = _time.split(":")
        _date = _date.split(" ")
        return self.tz.localize(
            datetime(
                int(_date[2]),
                self.months[_date[1]],
                int(_date[0]),
                int(_time[0]),
                int(_time[1]),
            )
        )
