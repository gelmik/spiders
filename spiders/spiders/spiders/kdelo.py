import scrapy


class KdeloSpider(scrapy.Spider):
    name = "kdelo"
    allowed_domains = ["www.kdelo.ru"]
    start_urls = ["https://www.kdelo.ru/news"]
    news_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "robin=32bfa195545e4cd2a753f0820d4a42fa40fec77abd724253b7cccd362f8dcfff; ASE_PHPSESSID=oc2c120006vj0u58gj7t2i5khu; ASE_YII_CSRF_TOKEN=dVZEZ2ZBbjY1WVlsbDI2OVlpV01qSTU1c3hfQUZSOWP-eFZ3GhqpAr2TKh9QhS2MQ4uAskhrmM-8Ldf3JRRWDA%3D%3D; amnesty=robinSameSite; tmr_reqNum=33; tmr_lvid=4fb87e41ac540823be9e0e8de09e5be4; tmr_lvidTS=1616521610066; _ym_uid=1616521612327351550; _ym_d=1616521612; __utma=217746576.1194874541.1616521612.1616521612.1616524174.2; __utmc=217746576; __utmz=217746576.1616521612.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ym_isad=2; tmr_detect=0%7C1616524183236; __gads=ID=351ee1f1e3daf87d-22f68e61daba0077:T=1616521620:RT=1616521620:S=ALNI_MZFBdWV3uaW3VHnZ3ZwltJlqSJzLA; __lxGr__ses=1pz2nkyk4gagg0k417319853; __lxGr__var_600413=_600413; __lxGr__var_600412=_600412; __lxGr__var_661432=_661439; __lxGr__var_668479=_668478; __utmb=217746576.2.10.1616524174; __utmt=1; swReg_delay=denial; ASE_anonymousId=219b963f2fe23b583e661f0ce2f5cec7; ASE_userLastVisit=2021-03-23+21%3A29%3A38; deadpool=19f8cfd9-6066-49b8-905f-e43fb5fae189",
        "Host": "www.kdelo.ru",
        "Referer": "https://www.kdelo.ru/",
        "Upgrade-Insecure-Requests": 1,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }

    def start_requests(self):
        yield scrapy.Request("https://www.kdelo.ru/news", headers=self.news_headers)

    def parse(self, response):
        print(response.body)
