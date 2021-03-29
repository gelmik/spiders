import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz
from scrapy.spiders import CrawlSpider


class RussianewsInfoSpider(scrapy.Spider):
    name = "russianews.info"
    description = "ссылки на новости через запрос с cookies"
    allowed_domains = ["russianews.info"]
    page = 1
    days = 7
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Host": "russianews.info",
        "Referer": "http://russianews.info/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36 OPR/74.0.3911.218 (Edition Yx 05)",
        "X-Requested-With": "XMLHttpRequest",
    }
    tz = pytz.timezone("Europe/Moscow")
    next_page = True

    def start_requests(self):
        yield scrapy.Request(
            "http://russianews.info/wp-admin/admin-ajax.php?action=jumla_load_more&nonce=67826fcf5e&page=1&post_type=post",
            headers=self.headers,
            cookies={"beget": "begetok"},
        )

    def parse(self, response):
        data = HtmlResponse(
            url="",
            body="\n".join(json.loads(response.body)["data"]["content"]).strip(),
            encoding="utf-8",
        )
        for href in data.xpath("//a[contains(@class , 'btn')]/@href").extract():
            yield scrapy.Request(
                href,
                callback=self.parse_artcle,
                headers=self.headers,
                cookies={"beget": "begetok"},
                meta={"url": href},
            )
        if self.next_page:
            self.page += 1
            yield scrapy.Request(
                f"http://russianews.info/wp-admin/admin-ajax.php?action=jumla_load_more&nonce=67826fcf5e&page={self.page}&post_type=post",
                headers=self.headers,
                cookies={"beget": "begetok"},
            )
        else:

            raise self.CloseSpider("Some Text")

    def parse_artcle(self, response):
        raw_date = response.xpath("//time/@datetime").extract()[0].split("+")[0]
        publish_date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
        if (datetime.now() - publish_date).days <= self.days:
            yield {
                "request_url": response.url,
                "url": response.meta["url"],
                "title": response.xpath("//h1[@class='entry-title']/text()").extract()[
                    0
                ],
                "text": " ".join(
                    response.xpath(
                        "//div[contains(@class, 'clearfix')]//*[not(self::script)]/text()"
                    ).extract()
                ),
                "raw_date": raw_date,
                "publish_date": self.tz.localize(publish_date),
                "author": None,
            }
        else:
            self.next_page = False
