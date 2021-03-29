import scrapy
import json
from datetime import datetime
from scrapy.http import HtmlResponse


class PochtaSpider(scrapy.Spider):
    name = "pochta"
    description = "сайт с json запросом в котором есть все новости, нет необходимости переходить на страницы отдельно"
    allowed_domains = ["www.pochta.ru"]
    page = 0
    start_urls = [
        f"https://www.pochta.ru/news-list?p_p_id=newsPortlet_WAR_portalportlet&p_p_lifecycle=2&p_p_state"
        f"=normal&p_p_mode=view&p_p_resource_id=news.find-list&p_p_cacheability=cacheLevelPage&p_p_col_id"
        f"=column-1&p_p_col_count=1&page={0}&size=5"
    ]

    def parse(self, response):
        data = json.loads(response.body)
        articles = data["journalArticles"]["articles"]
        for article in articles:
            raw_date = article["displayDate"]
            publish_date = datetime(
                int(raw_date.split("-")[0]),
                int(raw_date.split("-")[1]),
                int(raw_date.split("-")[2]),
            )
            yield {
                "request_url": f"https://www.pochta.ru/news-list?p_p_id=newsPortlet_WAR_portalportlet&p_p_lifecycle"
                f"=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=news.find-list&p_p_cacheability"
                f"=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1&page={self.page}&size=5",
                "url": response.url,
                "title": article["title"],
                "raw_date": raw_date,
                "publish_date": publish_date,
                "text": "\n".join(
                    HtmlResponse(url="", body=article["fullContent"], encoding="utf-8")
                    .xpath("//p/text()")
                    .extract()
                ),
                "author": None,
            }
        last_raw_date = articles[-1]["displayDate"]
        if (
            datetime.now()
            - datetime(
                int(last_raw_date.split("-")[0]),
                int(last_raw_date.split("-")[1]),
                int(last_raw_date.split("-")[2]),
            )
        ).days <= 30:
            self.page += 1
            yield scrapy.Request(
                url=f"https://www.pochta.ru/news-list?p_p_id=newsPortlet_WAR_portalportlet&p_p_lifecycle"
                f"=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=news.find-list&p_p_cacheability"
                f"=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1&page={self.page}&size=5"
            )
