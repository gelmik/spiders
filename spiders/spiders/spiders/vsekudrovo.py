import scrapy


class VsekudrovoSpider(scrapy.Spider):
    name = "vsekudrovo"
    description = "новости в корневом каталоге с пагинацией"
    allowed_domains = ["www.vsekudrovo.ru"]
    start_urls = ["https://www.vsevkudrovo.ru/news"]

    def parse(self, response):
        pass
