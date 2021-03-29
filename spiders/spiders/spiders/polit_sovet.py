import scrapy
from datetime import datetime


def convert_to_normal_text(text):
    return text.encode("cp1251", "replace").decode("utf8", "replace")


class PolitSovetSpider(scrapy.Spider):
    name = "polit-sovet"
    description = "сайт с кодировкой 1251"
    allowed_domains = ["polit-sovet.ru"]
    start_urls = ["http://polit-sovet.ru/blogs/news"]
    page = 1
    visited_urls = []

    def parse(self, response):

        for href in response.xpath(
            "//div[@class='root_container container_bg']//div[@class='left ml10']//h5/a/@href"
        ).extract():
            href = response.urljoin(href)
            print("*" * 1000)
            print(href)
            print("*" * 1000)
            if href not in self.visited_urls:
                self.visited_urls.append(href)
                yield scrapy.Request(
                    href, meta={"request_url": href}, callback=self.parse_article
                )
        last_raw_date = (
            response.xpath(
                "/html/body/div[2]/div[2]/div/div[1]/div[3]//div[@class='quiet fs10 mb10 acenter']/text()[last()]"
            )
            .extract()[-1]
            .split("/")
        )
        last_date = datetime(2021, int(last_raw_date[1]), int(last_raw_date[0]))
        if (datetime.now() - last_date).days <= 7:
            url = response.xpath(
                '//div[@class="right pager"]/a[last()]/@href'
            ).extract()[0]
            yield scrapy.Request(response.urljoin(url))

    def parse_article(self, response):
        title = convert_to_normal_text(
            response.xpath("//h1[@class='ml5 mb5']/text()").extract()[0]
        )
        raw_date = convert_to_normal_text(
            " ".join(
                response.xpath(
                    '//div[@class="ml5 fs11 quiet mb5"]//text()[last()]'
                ).extract()[::-1]
            )[2:]
        )
        text = convert_to_normal_text(
            " ".join(response.xpath("//div[@class='left ml10 mt5']//text()").extract())
        )
        publish_date = datetime(
            datetime.now().year,
            int(raw_date.split(" ")[0].split("/")[1]),
            int(raw_date.split(" ")[0].split("/")[0]),
            int(raw_date.split(" ")[1].split(":")[0]),
            int(raw_date.split(" ")[1].split(":")[1]),
        )
        yield {
            "url": response.url,
            "request_url": response.meta["request_url"],
            "title": title,
            "text": text,
            "raw_date": raw_date,
            "publish_date": publish_date,
            "author": None,
        }
