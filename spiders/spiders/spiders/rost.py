import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class RostSpider(scrapy.Spider):
    name = "rost.ru"
    allowed_domains = ["rost.ru"]
    start_urls = [
        "https://rost.ru/local/components/galior/publications.list/templates/.default/ajax.php?request=get_news&validation=1&navigation%5Bper_page%5D=24&filter%5BPROPERTY_RUBRIC%5D=3047&filter%5BIBLOCK_SECTION_ID%5D=2864&load_all_pages=true&page_from=1"
    ]
    description = "новости в json формате"
    page = 1
    date_now = datetime.now().date()
    days = 7
    visited_urls = []

    def parse(self, response):
        posts = json.loads(response.body)["posts"]
        for post in posts:
            raw_date = post["DATE_CREATE"]
            publish_date = datetime.strptime(raw_date, "%d.%m.%Y %H:%M:%S")
            href = f"https://rost.ru/presscenter/posts/{post['CODE']}"
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield {
                    "url": href,
                    "request_url": response.url,
                    "title": post["NAME"],
                    "text": "\n".join(
                        HtmlResponse(url="", body=post["DETAIL_TEXT"], encoding="utf-8")
                        .xpath("//text()")
                        .extract()
                    ),
                    "raw_date": raw_date,
                    "publish_date": publish_date,
                    "author": None,
                }
        if (
            self.date_now
            - datetime.strptime(posts[-1]["DATE_CREATE"], "%d.%m.%Y %H:%M:%S").date()
        ).days <= self.days:
            self.page += 1
            yield scrapy.Request(
                f"https://rost.ru/local/components/galior/publications.list/templates/.default/ajax.php?request=get_news&validation=1&navigation%5Bper_page%5D=24&navigation%5Bpage%5D={self.page}&filter%5BPROPERTY_RUBRIC%5D=3047&filter%5BIBLOCK_SECTION_ID%5D=2864"
            )
