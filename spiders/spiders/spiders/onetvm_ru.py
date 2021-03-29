import scrapy
from datetime import datetime, timedelta
from scrapy.http import HtmlResponse
import pytz

class OnetvmRuSpider(scrapy.Spider):
    name = 'onetvm.ru'
    allowed_domains = ['onetvm.ru']
    start_urls = ['https://onetvm.ru/novosti-den?page=1']
    description = "новости в корневом каталоге с пагинацией"
    page = 1
    date_now = datetime.now().date()
    days = 7
    visited_urls = []
    months = {
        "января": 1,
        "февраля": 2,
        "марта": 3,
        "апреля": 4,
        "мая": 5,
        "июня": 6,
        "июля": 7,
        "августа": 8,
        "сентября": 9,
        "октября": 10,
        "ноября": 11,
        "декабря": 12,
    }
    tz = pytz.timezone("Europe/Moscow")

    def parse(self, response):
        divs = response.xpath("//div[@class='custom-item']").extract()
        for div in divs:
            div = HtmlResponse(url='',body=div,encoding="utf-8")
            href = div.xpath("//div[@class = 'view-11']/a/@href").extract()[0]
            raw_article_date = div.xpath("//div[@class = 'view-15']/text()").extract()[0]
            if raw_article_date.split(' ')[0] == 'сегодня':
                publish_article_date = datetime.now().replace(hour=int(raw_article_date.split(' ')[1].split(':')[0]), minute=int(raw_article_date.split(' ')[1].split(':')[1]))
            elif raw_article_date.split(' ')[0] == 'вчера':
                publish_article_date = datetime.now().replace(hour=int(raw_article_date.split(' ')[1].split(':')[0]), minute=int(raw_article_date.split(' ')[1].split(':')[1])) - timedelta(days=1)
            else:
                publish_article_date = datetime(self.date_now.year, self.months[raw_article_date.split(' ')[1]], int(raw_article_date.split(' ')[0]), int(raw_article_date.split(' ')[2].split(':')[0]), int(raw_article_date.split(' ')[2].split(':')[1]))

            if (self.date_now - publish_article_date.date()).days <= self.days and href not in self.visited_urls:
                yield scrapy.Request(response.urljoin(href), callback=self.parse_article, meta={'raw_date': raw_article_date, 'publish_date': publish_article_date})
            else:
                break
        last_raw_date = HtmlResponse(url='',body=divs[-1],encoding="utf-8").xpath("//div[@class = 'view-15']/text()").extract()[0]
        last_article_date = datetime(self.date_now.year, self.months[last_raw_date.split(' ')[1]], int(last_raw_date.split(' ')[0])).date()
        if (self.date_now - last_article_date).days <= self.days:
            self.page += 1
            yield scrapy.Request(f"https://onetvm.ru/novosti-den?page={self.page}")

    def parse_article(self, response):
        yield {
            'url': response.url,
            'request_url' : response.url,
            'title': response.xpath("//h1/text()").extract()[0],
            'text': "\n".join(response.xpath("//div[@class = 'news-text']//text()").extract()),
            'raw_date': response.meta['raw_date'],
            'publish_date': response.meta['publish_date'],
            'author': None
        }