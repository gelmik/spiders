import scrapy


class KomDirSpider(scrapy.Spider):
    name = "kom-dir"
    allowed_domains = ["www.kom-dir.ru"]
    start_urls = ["https://www.kom-dir.ru/news"]
    news_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Cookie": "robin=487fd469587d4ad1b0e8940a4f4af728f4d004f63a1e4f9ebedfedef8dee68f0; "
        "ASE_PHPSESSID=o6ot6jksolhlta8pcggi3m39aj; "
        "ASE_YII_CSRF_TOKEN"
        "=YWlrZk1ZdVE1NDNIUmhWWW1JczdPd0FOaEljYmhyak7YsFERboHD2dHXZsFAUYWLLhqyKRFUU9qKPTUNqsXl0A%3D%3D; "
        "_ym_uid=1616337547541303815; _ym_d=1616337547; _ym_isad=1; __utmc=145596722; "
        "__utmz=145596722.1616337547.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); "
        "amnesty=robinSameSite; ASE_windowTypeCounter=%7B%22bpn%22%3A1%7D; "
        "ASE_WindowShowedPeriod_231=2021-03-21%2017%3A39%3A03",
        "Connection": "keep-alive",
        "Host": "www.kom-dir.ru",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/88.0.4324.192 Safari/537.36 OPR/74.0.3911.218 (Edition Yx 05) ",
    }

    def start_requests(self):
        yield scrapy.Request("https://www.kom-dir.ru/news", headers=self.news_headers)

    def parse(self, response):
        print(response.body)
        for href in response.xpath(
            "//a[@class = 'defaultBlock__itemTitleLink']/@href"
        ).extract():
            print(href)
