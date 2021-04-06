import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class ThebellSpider(scrapy.Spider):
    name = "thebell"
    allowed_domains = ["thebell.io"]
    start_urls = [
        "https://thebell.io/api/v1/layout_theme_data/?route=category&param=news&last_post_id=&index=1&count=3&lang=ru&isAdmin=&accepted_data_theme_id=&accepted_data_preset_id="
    ]
    description = "новости через api"
    index = 1
    count = 3
    date_now = datetime.now().date()
    days = 7
    visited_urls = []
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        data = json.loads(response.body)["data"]
        last_date = None
        for dat in data:
            for item in dat:
                item = item["item"]
                url = f"https://thebell.io/{item['slug']}"
                raw_date = item["publish_date"]
                publish_date = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
                if last_date is None:
                    last_date = publish_date
                elif last_date > publish_date:
                    last_date = publish_date
                if (
                    self.date_now - publish_date.date()
                ).days <= self.days and url not in self.visited_urls:
                    yield scrapy.Request(
                        f"https://thebell.io/api/v1/layout_theme_data/?route=post&param={item['slug']}&last_post_id=&index=1&count=3&lang=ru&isAdmin=&accepted_data_theme_id=&accepted_data_preset_id=&excludePosts=&exec=&postCount=",
                        callback=self.parse_article,
                        meta={
                            "url": url,
                            "raw_date": raw_date,
                            "publish_date": publish_date,
                        },
                    )
        if (self.date_now - last_date.date()).days <= self.days:
            self.index += self.count
            yield scrapy.Request(
                f"https://thebell.io/api/v1/layout_theme_data/?route=category&param=news&last_post_id=&index={self.index}&count={self.count}&lang=ru&isAdmin=&request_chain_params=%7B\"last_post_id\":{data[-1][-1]['item']['id']}%7D"
            )

    def parse_article(self, response):
        data = json.loads(response.body)["data"][0][0]["item"]
        yield {
            "url": response.meta["url"],
            "request_url": response.url,
            "title": data["title"],
            "text": "\n".join(
                HtmlResponse(url="", body=data["content"], encoding="utf-8")
                .xpath("//text()")
                .extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
