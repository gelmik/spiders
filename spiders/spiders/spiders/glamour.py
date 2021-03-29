import scrapy
import json
from datetime import datetime


class GlamourSpider(scrapy.Spider):
    name = "glamour"
    description = "json выдается через api на каждую новость"
    allowed_domains = ["api.glamour.ru"]
    offset = 0
    visited_urls = []

    def start_requests(self):
        yield scrapy.Request(
            f"https://api.glamour.ru/post/main?_limit=5&_offset={self.offset}&_order_dir=DESC"
            f"&_order_by=publishedAt"
        )

    def parse(self, response):
        data = json.loads(response.body)
        for item in data:
            try:
                href = f"https://api.glamour.ru/article/{item['slug']}?"
            except:
                continue
            item_date = datetime.strptime(
                item["published_at"].split("+")[0], "%Y-%m-%dT%H:%M:%S"
            )
            if (datetime.now() - item_date).days <= 7 and href not in self.visited_urls:
                yield scrapy.Request(
                    href,
                    meta={
                        "request_url": f"https://www.glamour.ru/{item['main_tag']['slug']}/{item['slug']}"
                    },
                    callback=self.parse_article,
                )
        last_date = datetime.strptime(
            data[-1]["published_at"].split("+")[0], "%Y-%m-%dT%H:%M:%S"
        )
        if (datetime.now() - last_date).days <= 7:
            self.offset += 5
            yield scrapy.Request(
                f"https://api.glamour.ru/post/main?_limit=5&_offset={self.offset}&_order_dir=DESC"
                f"&_order_by=publishedAt"
            )

    def parse_article(self, response):
        data = json.loads(response.body)
        raw_date = data["published_at"].split("+")[0]
        publish_date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
        text = ""
        for item in data["formatted_content"]["blocks"]:
            if item["type"] == "text_wide":
                text += item["content"]["text"]
            elif item["type"] == "inset_wide":
                text += item["content"]["inset"]
            else:
                continue
        yield {
            "request_url": response.meta["request_url"],
            "url": response.url,
            "title": data["name"],
            "raw_date": raw_date,
            "publish_date": publish_date,
            "text": text,
            "author": None,
        }
