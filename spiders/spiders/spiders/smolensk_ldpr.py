import scrapy
import json
from datetime import datetime
from bs4 import BeautifulSoup


class SmolenskLdprSpider(scrapy.Spider):
    name = "smolensk_ldpr"
    allowed_domains = ["smolensk.ldpr.ru"]
    quotes_base_url = "https://smolensk.ldpr.ru/api/pb/articles?site_key=smolensk&aggregate=full&limit=12&page=%s"
    page = 1
    start_urls = [quotes_base_url % 1]

    def parse(self, response):

        data = json.loads(response.body)
        if data["simple"] != None:
            for result in data["simple"]:
                print(BeautifulSoup(result["content"], "lxml").text)
                text = BeautifulSoup(result["content"], "lxml").text
                yield {
                    "url": response.urljoin(f"/event/{result['id']}"),
                    "title": result["title"],
                    "text": text,
                    "raw_date": result["created_at"],
                    "publish_date": datetime.strptime(
                        result["created_at"][:-1], "%Y-%m-%dT%H:%M:%S.%f"
                    ),
                }
            self.page += 1
            yield scrapy.Request(self.quotes_base_url % self.page)
