import scrapy
from datetime import datetime


class ItepSpider(scrapy.Spider):
    name = 'itep'
    allowed_domains = ['www.itep.ru']
    start_urls = ['http://www.itep.ru/news/']

    def parse(self, response):
        for href, title in zip(response.xpath("//div[@class = 'news-list']/p[@class = 'news-item']/a/@href").extract(),
                              response.xpath("//div[@class = 'news-list']/p[@class = 'news-item']/a/b/text()").extract()):
            print(href)
            url = response.urljoin(href)
            print(url)
            yield scrapy.Request(url, callback=self.article_parse, meta={'title': title})
        next_page = response.xpath("//font[@class = 'text']/a[last() - 1]/text()").get()
        if next_page == ">>":
            yield scrapy.Request(
                response.urljoin(response.xpath("//font[@class = 'text']/a[last() - 1]/@href").get()),
                callback=self.parse)

    def article_parse(self, response):
        date = response.xpath("//span[@class = 'news-date-time']/text()").get()
        yield {
            'url': response.url,
            'title': response.meta['title'],
            'text': ''.join(response.xpath("//div[@class = 'news-detail']//text()").getall()),
            'publish_date': datetime(int(date.split('.')[2]), int(date.split('.')[1]), int(date.split('.')[0])),
            'raw_date': date
        }
