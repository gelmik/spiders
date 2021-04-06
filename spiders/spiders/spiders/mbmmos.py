import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class MbmmosSpider(scrapy.Spider):
    name = "mbm.mos.ru"
    allowed_domains = ["mbm.mos.ru"]
    page = 1
    count = 10
    description = "новости через api в json"
    visited_urls = []
    days = 7
    date_now = datetime.now().date()
    tz = pytz.timezone("Europe/Moscow")

    def start_requests(self):
        form_data = {
            "action": "getList",
            "count": "10",
            "filters": {"themes": []},
            "include": ["commentsCount", "theme"],
            "model": "news",
            "page": "1",
        }
        yield scrapy.FormRequest(url="https://mbm.mos.ru/api/", formdata=form_data)

    def parse(self, response):
        data = json.loads(response.body)["data"]["items"]
        for article in data:
            raw_date = article["date"]
            publish_date = datetime.strptime(raw_date, "%d.%m.%Y %H:%M:%S")
            if (self.date_now - publish_date.date()).days <= self.days:
                href = "https://mbm.mos.ru/" + article["url"]
                if href not in self.visited_urls:
                    yield {
                        "url": href,
                        "request_url": response.url,
                        "title": article["name"],
                        "text": "".join(
                            HtmlResponse(
                                url="", body=article["detail_text"], encoding="utf-8"
                            )
                            .xpath("//text()")
                            .extract()
                        ),
                        "raw_date": raw_date,
                        "publish_date": publish_date,
                        "author": None,
                    }
        last_date = datetime.strptime(data[-1]["date"], "%d.%m.%Y %H:%M:%S").date()
        if (self.date_now - last_date).days <= self.days:
            self.page += 1
            form_data = {
                "action": "getList",
                "count": "10",
                "filters": {"themes": []},
                "include": ["commentsCount", "theme"],
                "model": "news",
                "page": str(self.page),
            }
            yield scrapy.FormRequest(url="https://mbm.mos.ru/api/", formdata=form_data)
