import scrapy
import json
from datetime import datetime, timedelta
import pytz
import re


class CbondsSpider(scrapy.Spider):
    def clean_text(self, text):
        text = text.replace(u"\xa0", u" ")
        text.strip()
        return re.sub(r"(\s){2,}", "\\1", text)

    name = "cbonds.ru"
    allowed_domains = ["cbonds.ru"]
    start_urls = ["https://cbonds.ru/news/"]
    tz = pytz.timezone("Europe/Moscow")
    start_payload = {
        "filters": [
            {"field": "show_all", "operator": "eq", "value": 1},
            {"field": "language", "operator": "in", "value": ["rus"]},
            {
                "field": "date",
                "operator": "ge",
                "value": (datetime.today() - timedelta(days=14)).strftime("%Y-%m-%d"),
            },
            {
                "field": "section_id",
                "operator": "in",
                "value": [str(i) for i in range(1, 1000)],
            },
        ],
        "sorting": [],
        "quantity": {"offset": 0, "limit": 30},
        "lang": "rus",
    }

    start_headers = {
        "Host": "cbonds.ru",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": "CBONDSSESSID=a282126b573fa484860a7a437716f45f; _ga=GA1.2.1371979517.1616522492; _gid=GA1.2.2095803655.1616522492",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://cbonds.ru",
        "Connection": "keep-alive",
        "Referer": "https://cbonds.ru/news/",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
    }

    def start_requests(self):
        yield scrapy.Request(
            url="https://cbonds.ru/news/",
            method="POST",
            body=json.dumps(self.start_payload),
            headers=self.start_headers,
            callback=self.parse,
        )

    def parse(self, response):
        data = json.loads(response.body)["response"]["items"]
        for item in data:
            if (datetime.now() - datetime.strptime(item["date"], "%d.%m.%Y")).days <= 7:
                yield {
                    "url": item["cb_link"],
                    "request_url": "https://cbonds.ru/news/",
                    "title": self.clean_text(item["caption"]),
                    "text": self.clean_text(item["text"]),
                    "raw_date": item["date_time"],
                    "publish_date": self.tz.localize(
                        datetime.strptime(item["date_time"], "%d.%m.%Y %H:%M:%S")
                    ),
                    "author": None,
                }
        last_date = datetime.strptime(data[-1]["date"], "%d.%m.%Y")
        if (datetime.now() - last_date).days <= 7:
            self.start_payload["quantity"]["offset"] += 30
            yield scrapy.Request(
                url="https://cbonds.ru/news/",
                method="POST",
                body=json.dumps(self.start_payload),
                headers=self.start_headers,
                callback=self.parse,
            )
