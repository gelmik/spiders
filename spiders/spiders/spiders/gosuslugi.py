import scrapy
import json
from datetime import datetime, date, timedelta
from scrapy.http import HtmlResponse


class GosuslugiSpider(scrapy.Spider):
    name = "www.gosuslugi.ru"
    description = "json выдается через api на каждую новость со стартовой новостью с query промежутком от начальной даты до конечной"
    allowed_domains = ["www.gosuslugi.ru"]
    visited_urls = []

    def start_requests(self):
        startDate = ".".join(
            [part for part in str(date.today() - timedelta(days=180)).split("-")[::-1]]
        )
        endDate = ".".join([part for part in str(date.today()).split("-")[::-1]])
        href = f"https://www.gosuslugi.ru/api/cms/v1/news?_=1616340618385&endDate={endDate}&page=1&personType=PERSON&region=45000000000&size=100&startDate={startDate}"
        yield scrapy.Request(href)

    def parse(self, response):
        data = json.loads(response.body)["data"]
        for item in data:
            href = f"https://www.gosuslugi.ru/api/cms/v1/news/{item['code']}"
            if href not in self.visited_urls:
                self.visited_urls.append(href)
                yield scrapy.Request(
                    url=href, meta={"request_url": href}, callback=self.parse_article
                )

    def parse_article(self, response):
        data = json.loads(response.body)
        raw_date = data["pubDate"].split(".")[0]
        publish_date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
        yield {
            "request_url": response.meta["request_url"],
            "url": response.url,
            "title": data["title"],
            "raw_date": raw_date,
            "publish_date": publish_date,
            "text": "\n".join(
                HtmlResponse(url="", body=data["text"], encoding="utf-8")
                .xpath("//p//text()")
                .extract()
            ),
            "author": None,
        }
