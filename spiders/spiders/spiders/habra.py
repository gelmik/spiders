import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse
import pytz


class HabraSpider(scrapy.Spider):
    name = "habra"
    allowed_domains = ["habra.js.org", "m.habr.com"]
    start_urls = ["https://m.habr.com/kek/v2/articles?fl=ru&hl=ru&news=true&page=1"]
    description = "новости в json формате"
    page = 1
    date_now = datetime.now().date()
    days = 7
    visited_urls = []
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        data = json.loads(response.body)["articleRefs"]
        articles = []
        for key in data:
            articles.append(data[key])
        last_date = None
        for article in articles:
            raw_date = article["timePublished"].split("+")[0]
            publish_date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
            if last_date is None:
                last_date = publish_date
            elif last_date > publish_date:
                last_date = publish_date
            href = f"https://m.habr.com/kek/v2/articles/{article['id']}?fl=ru&hl=ru"
            if (
                self.date_now - publish_date.date()
            ).days <= self.days and href not in self.visited_urls:
                yield scrapy.Request(
                    href,
                    callback=self.parse_artcile,
                    meta={
                        "raw_date": raw_date,
                        "publish_date": publish_date,
                        "url": f"https://habra.js.org/post/{article['id']}",
                    },
                    headers={"Referer": f"https://habra.js.org/post/{article['id']}"},
                )
        if (self.date_now - last_date.date()).days <= self.days:
            self.page += 1
            yield scrapy.Request(
                f"https://m.habr.com/kek/v2/articles?fl=ru&hl=ru&news=true&page={self.page}"
            )

    def parse_artcile(self, response):
        data = json.loads(response.body)
        yield {
            "url": response.meta["url"],
            "request_url": response.url,
            "title": data["titleHtml"],
            "text": " ".join(
                HtmlResponse(url="", body=data["textHtml"], encoding="utf-8")
                .xpath("//text()")
                .extract()
            ),
            "raw_date": response.meta["raw_date"],
            "publish_date": response.meta["publish_date"],
            "author": None,
        }
