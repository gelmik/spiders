import scrapy
import json
from datetime import datetime


class TdailyRuSpider(scrapy.Spider):
    name = "tdaily.ru"
    allowed_domains = ["tdaily.ru"]
    start_urls = [
        "https://tdaily.ru/api/news/rubric/mtt-pro-business",
        "https://tdaily.ru/api/news/rubric/science",
        "https://tdaily.ru/api/news/rubric/retail",
        "https://tdaily.ru/api/news/rubric/payments",
        "https://tdaily.ru/api/news/rubric/ideas",
        "https://tdaily.ru/api/news/rubric/content",
        "https://tdaily.ru/api/news/rubric/conference",
        "https://tdaily.ru/api/news/rubric/analytics",
        "https://tdaily.ru/api/news/rubric/svyaz",
        "https://tdaily.ru/api/news/rubric/hosting",
        "https://tdaily.ru/api/news/rubric/tests",
        "https://tdaily.ru/api/news/rubric/interview",
        "https://tdaily.ru/api/news/rubric/comfort",
        "https://tdaily.ru/api/news/rubric/auto",
    ]
    days = 7

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.FormRequest(
                url + "/0/15", meta={"rubric": url, "offset": 0, "size": 15}
            )

    def parse(self, response):
        data = json.loads(response.body)
        now = datetime.now().date()
        if data[0]["id"] != "":
            for part in data:
                publish_date = datetime.strptime(part["publishAt"], "%d.%m.%Y %H:%M")
                if (now - publish_date.date()).days <= self.days:
                    yield scrapy.Request(
                        f"https://tdaily.ru/news/{part['urlAlias']}",
                        meta={
                            "url": f"https://tdaily.ru/news/{part['urlAlias']}",
                            "publish_date": publish_date,
                            "raw_date": part["publishAt"],
                        },
                        callback=self.parse_article,
                    )
            last_date = datetime.strptime(
                data[-1]["publishAt"], "%d.%m.%Y %H:%M"
            ).date()
            if (now - last_date).days <= self.days:
                yield scrapy.Request(
                    f"{response.meta['rubric']}/{response.meta['size'] + response.meta['offset']}/6",
                    meta={
                        "rubric": response.meta["rubric"],
                        "offset": response.meta["size"] + response.meta["offset"],
                        "size": 6,
                    },
                )

    def parse_article(self, response):
        title = response.xpath("//h1[@class = 'title']/text()").extract()[0]
        text = "\n".join(
            response.xpath(
                "//div[contains(@class , 'news-item')]//div[@class='content']//text()"
            ).extract()
        )
        yield {
            "url": response.meta["url"],
            "request_url": response.url,
            "title": title,
            "text": text,
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
