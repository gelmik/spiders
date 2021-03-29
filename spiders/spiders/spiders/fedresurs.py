import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse


class FedresursSpider(scrapy.Spider):
    name = "fedresurs.ru"
    allowed_domains = ["fedresurs.ru"]
    start_urls = ["https://fedresurs.ru/backend/news/?pageSize=15&startIndex=0"]
    description = ""
    visited_urls = []
    startIndex = 0
    page_headers = {
        "Accept": "application/json, text/plain, */*",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://fedresurs.ru/news?attempt=1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36 OPR/74.0.3911.218 (Edition Yx 05)",
    }
    article_headers = {
        "Accept": "application/json, text/plain, */*",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": None,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36 OPR/74.0.3911.218 (Edition Yx 05)",
    }

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.page_headers)

    def parse(self, response):
        data = json.loads(response.body)

        for article in data:
            href = "https://fedresurs.ru/backend/news/" + article["guid"]
            article_date = datetime.strptime(
                article["datePublish"].split(".")[0], "%Y-%m-%dT%H:%M:%S"
            )
            if (
                href not in self.visited_urls
                and len(self.visited_urls) <= 1000
                and (datetime.now() - article_date).days <= 30
            ):
                self.visited_urls.append(href)
                self.article_headers["Referer"] = href
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={"request_url": href},
                    headers=self.article_headers,
                )
        if (
            datetime.now()
            - datetime.strptime(
                data[-1]["datePublish"].split(".")[0], "%Y-%m-%dT%H:%M:%S"
            )
        ).days <= 30:
            self.startIndex += 15
            yield scrapy.Request(
                f"https://fedresurs.ru/backend/news/?pageSize=15&startIndex={self.startIndex}",
                headers=self.page_headers,
            )

    def parse_article(self, response):
        data = json.loads(response.body)
        yield {
            "url": response.url,
            "request_url": response.meta["request_url"],
            "title": data["title"],
            "text": "\n".join(
                HtmlResponse(url="", body=data["body"], encoding="utf-8")
                .xpath("//text()")
                .extract()
            ),
            "publish_date": datetime.strptime(
                data["datePublish"].split(".")[0], "%Y-%m-%dT%H:%M:%S"
            ),
            "raw_date": data["datePublish"],
            "author": None,
        }
