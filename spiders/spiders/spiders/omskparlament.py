import scrapy
from datetime import datetime


class OmskparlamentSpider(scrapy.Spider):
    name = "omskparlament"
    allowed_domains = ["www.omsk-parlament.ru"]
    start_urls = ["http://www.omsk-parlament.ru/?doit=news"]
    page = 0

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

    def start_requests(self):
        frmdata = {
            "sPage": "0",
            "sSort": "0",
            "sDir": "0",
            "sevents": "0",
            "sdocs": "0",
            "snews": "1",
        }
        yield scrapy.FormRequest(
            url="http://www.omsk-parlament.ru/?doit=news", formdata=frmdata
        )

    def parse(self, response):
        for href, date in zip(
            response.xpath(
                "//div[@class = 'news_block eqblock row']//div[@class='news_anons_more']/a/@href"
            ).extract(),
            response.xpath(
                "//div[@class = 'news_block eqblock row']//div[@class='news_date']/text()"
            ).extract(),
        ):
            url = response.urljoin(href)

            yield scrapy.Request(url, callback=self.article_parse, meta={"date": date})

        last_page = int(
            response.xpath("//a[@class=  'paginate_button'][last()]/text()").get()
        )

        if last_page >= self.page + 1:
            self.page += 1
            frmdata = {
                "sPage": str(self.page),
                "sSort": "0",
                "sDir": "0",
                "sevents": "0",
                "sdocs": "0",
                "snews": "1",
            }
            yield scrapy.FormRequest(
                url="http://www.omsk-parlament.ru/?doit=news",
                formdata=frmdata,
                callback=self.parse,
                dont_filter=True,
            )

    def article_parse(self, response):

        date = response.meta["date"].split(" ")
        try:
            title = (
                response.xpath("//div[@class = 'newsheaderbig blue']/text()")
                .get()
                .strip()
            )
        except:
            title = "Отсутствует"
        yield {
            "url": response.url,
            "title": title,
            "text": "".join(
                response.xpath(
                    "//div[@class = 'eventblock']//node()[not(@class = 'newsheaderbig blue')]/text()"
                ).getall()
            ),
            "publish_date": datetime(int(date[2]), self.months[date[1]], int(date[0])),
            "raw_date": response.meta["date"],
        }
