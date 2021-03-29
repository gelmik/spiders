import scrapy
import json
from scrapy.http import HtmlResponse
from datetime import datetime


class A78RuSpider(scrapy.Spider):
    name = "78"
    description = "Сайт собирает данные отправкой полезной нагрузки на graphql"
    allowed_domains = ["78.ru"]
    start_urls = ["https://78.ru/api/graphql"]
    headers = {
        "Host": "78.ru",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://78.ru/news",
        "Content-Type": "application/json",
        "Origin": "https://78.ru",
        "Connection": "keep-alive",
        "Cookie": "tmr_reqNum=20; tmr_lvid=1d1ba3872f170f5e31e05ab363df51dc; tmr_lvidTS=1615814578948; _ym_uid=1615814580263242627; _ym_d=1615814580; _ga=GA1.2.800222994.1615814580; _gid=GA1.2.705915683.1615814580; _ym_isad=2; _a_d3t6sf=duny6Dy9ZLeEilk7k0jIWQfE; _fbp=fb.1.1615814580837.409895885; tmr_detect=0%7C1615830321070; cto_bundle=43dOiV9PZ3k4Mmo4TjN6MklyZ2FkSnZ2Und0UnpsVDh6MGN0dEZMMFBLMUFMQU9lb1B3d0d6Y2IzQUFnaUlYb1JXJTJCTnA0VHh5VlhLNW1JS1ZRb3RZQXljeDJFMFdDSiUyRkxleVB0UEtxQnRUTFd1MWRUMUU5NFBXOXJpNUFGUk1waENobEM3UVhmb1A2eDlYMUtpdXJERWs2WVRBJTNEJTNE; _grf_vis=1; _gat=1",
        "TE": "Trailers",
    }
    count = 0

    def start_requests(self):

        payload = {
            "query": "query NewsFeed_Query(\n  $section: ID!\n  $categorySlug: ID\n  $count: Int!\n  $after: String\n  $topic: ID!\n  $ignoreSection: Boolean\n  $author: ID\n  $date: String\n) {\n  viewer {\n    ...NewsFeedList_viewer_UGWLp\n    ...NewsgroupNavigation_viewer_1hrbBR\n    mycats: categories(section: $section, hidden: false) {\n      edges {\n        node {\n          name\n          slug\n          id\n        }\n      }\n    }\n    mysection: section(id: $section) {\n      name\n      id\n    }\n    mytopic: topic(id: $topic) {\n      name\n      id\n    }\n    id\n  }\n}\n\nfragment NewsFeedList_viewer_UGWLp on Viewer {\n  articles(first: $count, after: $after, section: $section, category: $categorySlug, hidden: false, topic: $topic, author: $author, date: $date, ignoreSection: $ignoreSection) {\n    edges {\n      node {\n        __typename\n        ...NewsFeedItem_article\n        id\n      }\n      cursor\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n    }\n  }\n}\n\nfragment NewsgroupNavigation_viewer_1hrbBR on Viewer {\n  categories(section: $section, hidden: false) {\n    edges {\n      node {\n        id\n        name\n        section\n        slug\n      }\n    }\n  }\n  section(id: $section) {\n    id\n    name\n  }\n}\n\nfragment NewsFeedItem_article on Article {\n  availableAt\n  slug\n  title\n  lead\n  authorName\n  author\n  section\n  previewAttribution\n  combinedPreviewVideo {\n    id\n    filename\n    description\n  }\n  preview {\n    filename\n    type\n    description\n    id\n  }\n  topics {\n    id\n    name\n    slug\n  }\n  ...LinkedArticles_article\n}\n\nfragment LinkedArticles_article on Article {\n  linkedArticles {\n    ...NewsgroupItem_newsgroup\n    id\n  }\n}\n\nfragment NewsgroupItem_newsgroup on Article {\n  id\n  slug\n  title\n  lead\n  categoryName\n  availableAt\n  preview {\n    filename\n    type\n    description\n    id\n  }\n  combinedPreviewVideo {\n    filename\n    type\n    description\n    id\n  }\n  authorName\n  section\n}\n",
            "variables": {
                "after": None,
                "author": None,
                "categorySlug": None,
                "count": 5,
                "date": None,
                "ignoreSection": False,
                "section": "U2VjdGlvbjo1OTg4YmM3MTNhODdiYzUyMDMwMzUyMzQ=",
                "topic": "",
            },
        }
        yield scrapy.Request(
            url="https://78.ru/api/graphql",
            method="POST",
            body=json.dumps(payload),
            headers=self.headers,
            callback=self.parse,
        )

    def parse(self, response):
        data = json.loads(response.body)
        for result in data["data"]["viewer"]["articles"]["edges"]:
            result_payload = {
                "query": "query ArticleQuery_Slug_Query(\n  $slug: String\n  $availableAt: String\n) {\n  todayNewsViewer: viewer {\n    ...TodayNews_viewer\n    id\n  }\n  viewer {\n    article(slug: $slug, availableAt: $availableAt) {\n      title\n      category\n      slug\n      lead\n      bodyHtml\n      authorName\n      author\n      availableAt\n      section\n      sectionName\n      id\n      categoryName\n      previewAttribution\n      combinedPreviewVideo {\n        id\n        filename\n        description\n      }\n      preview {\n        filename\n        description\n        type\n        status\n        alt\n        title\n        id\n      }\n      seoTitle\n      seoDescription\n      seoKeywords\n      topics {\n        id\n        name\n        slug\n      }\n      ...LinkedArticles_article\n    }\n    id\n  }\n}\n\nfragment TodayNews_viewer on Viewer {\n  ...CenterArticle_viewer\n  ...EventList_viewer\n}\n\nfragment LinkedArticles_article on Article {\n  linkedArticles {\n    ...NewsgroupItem_newsgroup\n    id\n  }\n}\n\nfragment NewsgroupItem_newsgroup on Article {\n  id\n  slug\n  title\n  lead\n  categoryName\n  availableAt\n  preview {\n    filename\n    type\n    description\n    id\n  }\n  combinedPreviewVideo {\n    filename\n    type\n    description\n    id\n  }\n  authorName\n  section\n}\n\nfragment CenterArticle_viewer on Viewer {\n  centerArticles: articles(first: 1, hidden: false, h: true) {\n    edges {\n      node {\n        title\n        slug\n        section\n        category\n        categoryName\n        authorName\n        preview {\n          filename\n          type\n          preview\n          id\n        }\n        combinedPreviewVideo {\n          filename\n          type\n          preview\n          id\n        }\n        availableAt\n        id\n      }\n    }\n  }\n}\n\nfragment EventList_viewer on Viewer {\n  events: articles(first: 5, hidden: false, e: true) {\n    edges {\n      node {\n        ...NewsgroupItem_newsgroup\n        id\n      }\n    }\n  }\n}\n",
                "variables": {
                    "availableAt": result["node"]["availableAt"].split("T")[0],
                    "slug": result["node"]["slug"],
                },
            }
            self.count += 1
            yield scrapy.Request(
                url="https://78.ru/api/graphql",
                method="POST",
                headers=self.headers,
                body=json.dumps(result_payload),
                callback=self.parse_article,
            )

        if (
            data["data"]["viewer"]["articles"]["pageInfo"]["hasNextPage"]
            and (
                datetime.now()
                - datetime.fromisoformat(
                    data["data"]["viewer"]["articles"]["edges"][-1]["node"][
                        "availableAt"
                    ].split(".")[0]
                )
            ).days
            <= 7
        ):
            headers = {
                "Host": "78.ru",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
                "Accept": "*/*",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://78.ru/news",
                "Content-Type": "application/json",
                "Origin": "https://78.ru",
                "Connection": "keep-alive",
                "Cookie": "tmr_reqNum=20; tmr_lvid=1d1ba3872f170f5e31e05ab363df51dc; tmr_lvidTS=1615814578948; "
                "_ym_uid=1615814580263242627; _ym_d=1615814580; _ga=GA1.2.800222994.1615814580; "
                "_gid=GA1.2.705915683.1615814580; _ym_isad=2; _a_d3t6sf=duny6Dy9ZLeEilk7k0jIWQfE; "
                "_fbp=fb.1.1615814580837.409895885; tmr_detect=0%7C1615830321070; "
                "cto_bundle"
                "=43dOiV9PZ3k4Mmo4TjN6MklyZ2FkSnZ2Und0UnpsVDh6MGN0dEZMMFBLMUFMQU9lb1B3d0d6Y2IzQUFnaUlYb1JXJTJCTnA0VHh5VlhLNW1JS1ZRb3RZQXljeDJFMFdDSiUyRkxleVB0UEtxQnRUTFd1MWRUMUU5NFBXOXJpNUFGUk1waENobEM3UVhmb1A2eDlYMUtpdXJERWs2WVRBJTNEJTNE; _grf_vis=1; _gat=1",
                "TE": "Trailers",
            }
            payload = {
                "query": "query NewsFeed_Query(\n  $section: ID!\n  $categorySlug: ID\n  $count: Int!\n  $after: "
                "String\n  $topic: ID!\n  $ignoreSection: Boolean\n  $author: ID\n  $date: String\n) {\n  "
                "viewer {\n    ...NewsFeedList_viewer_UGWLp\n    ...NewsgroupNavigation_viewer_1hrbBR\n    "
                "mycats: categories(section: $section, hidden: false) {\n      edges {\n        node {\n     "
                "     name\n          slug\n          id\n        }\n      }\n    }\n    mysection: section("
                "id: $section) {\n      name\n      id\n    }\n    mytopic: topic(id: $topic) {\n      "
                "name\n      id\n    }\n    id\n  }\n}\n\nfragment NewsFeedList_viewer_UGWLp on Viewer {\n  "
                "articles(first: $count, after: $after, section: $section, category: $categorySlug, "
                "hidden: false, topic: $topic, author: $author, date: $date, ignoreSection: $ignoreSection) "
                "{\n    edges {\n      node {\n        __typename\n        ...NewsFeedItem_article\n        "
                "id\n      }\n      cursor\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n    "
                "}\n  }\n}\n\nfragment NewsgroupNavigation_viewer_1hrbBR on Viewer {\n  categories(section: "
                "$section, hidden: false) {\n    edges {\n      node {\n        id\n        name\n        "
                "section\n        slug\n      }\n    }\n  }\n  section(id: $section) {\n    id\n    name\n  "
                "}\n}\n\nfragment NewsFeedItem_article on Article {\n  availableAt\n  slug\n  title\n  "
                "lead\n  authorName\n  author\n  section\n  previewAttribution\n  combinedPreviewVideo {\n   "
                " id\n    filename\n    description\n  }\n  preview {\n    filename\n    type\n    "
                "description\n    id\n  }\n  topics {\n    id\n    name\n    slug\n  }\n  "
                "...LinkedArticles_article\n}\n\nfragment LinkedArticles_article on Article {\n  "
                "linkedArticles {\n    ...NewsgroupItem_newsgroup\n    id\n  }\n}\n\nfragment "
                "NewsgroupItem_newsgroup on Article {\n  id\n  slug\n  title\n  lead\n  categoryName\n  "
                "availableAt\n  preview {\n    filename\n    type\n    description\n    id\n  }\n  "
                "combinedPreviewVideo {\n    filename\n    type\n    description\n    id\n  }\n  "
                "authorName\n  section\n}\n",
                "variables": {
                    "after": data["data"]["viewer"]["articles"]["pageInfo"][
                        "endCursor"
                    ],
                    "author": None,
                    "categorySlug": None,
                    "count": 5,
                    "date": None,
                    "ignoreSection": False,
                    "section": "U2VjdGlvbjo1OTg4YmM3MTNhODdiYzUyMDMwMzUyMzQ=",
                    "topic": "",
                },
            }
            yield scrapy.Request(
                url="https://78.ru/api/graphql",
                method="POST",
                body=json.dumps(payload),
                headers=headers,
            )

    def parse_article(self, response):
        data = json.loads(response.body)["data"]["viewer"]["article"]

        yield {
            "request_url": "https://78.ru/api/graphql",
            "url": f"https://78.ru/news/{data['availableAt'].split('T')[0]}/{data['slug']}",
            "title": data["title"],
            "text": "\n".join(
                HtmlResponse(url="", body=data["bodyHtml"], encoding="utf-8")
                .xpath("//p/text()")
                .extract()
            ),
            "publish_date": datetime.fromisoformat(data["availableAt"].split(".")[0]),
            "raw_date": data["availableAt"].split(".")[0],
            "author": None,
        }
