import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class DfmSpider(scrapy.Spider):
    name = "dfm"
    allowed_domains = ["dfm.ru"]
    start_urls = [
        "https://dfm.ru/api/news/news?page=1&per_page=6&order_by=is_popular&order_dir=desc&order_by_2=starts_at&order_dir_2=desc"
    ]
    page = 1
    description = "новости через api в json"
    visited_urls = []
    days = 7
    date_now = datetime.now().date()
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        data = json.loads(response.body)["items"]
        for item in data:
            raw_date = item["created_at"]
            publish_date = datetime.strptime(raw_date, "%Y-%m-%d %H:%M")
            if (self.date_now - publish_date.date()).days <= self.days:
                href = "https://dfm.ru/news/radio-news/" + item["slug"]
                if href not in self.visited_urls:
                    yield {
                        "url": href,
                        "request_url": response.url,
                        "title": item["name"],
                        "text": "\n".join(
                            HtmlResponse(url="", body=item["body"], encoding="utf-8")
                            .xpath("//text()")
                            .extract()
                        ),
                        "raw_date": raw_date,
                        "publish_date": publish_date,
                        "author": None,
                    }
        last_date = datetime.strptime(data[-1]["created_at"], "%Y-%m-%d %H:%M").date()
        if (self.date_now - last_date).days <= self.days:
            self.page += 1
            yield scrapy.Request(
                f"https://dfm.ru/api/news/news?page={self.page}&per_page=6&order_by=is_popular&order_dir=desc&order_by_2=starts_at&order_dir_2=desc"
            )
