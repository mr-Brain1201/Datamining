import scrapy

from avito_parse.loaders import AvitoLoader
from avito_parse.spiders.xpaths import AVITO_PAGE_XPATH, AVITO_FLAT_XPATH


class AvitoSpider(scrapy.Spider):
    name = "avito"
    allowed_domains = ["avito.ru"]
    start_urls = [
        "https://www.avito.ru/krasnodar/nedvizhimost"
    ]

    def _get_follow_xpath(self, response, xpath, callback):
        for url in response.xpath(xpath):
            yield response.follow(url, callback=callback, cookies={'VISITOR_INFO1_LIVE': '6OeaA1Iof6M', 's_gl': 'c2b7e804c78d5155b602c25657860b1ecwIAAABSVQ=='})

    def parse(self, response, **kwargs):
        callbacks = {
            "all_flats": self.parse, "pagination": self.parse,
            "flat": self.flat_parse
        }

        for key, xpath in AVITO_PAGE_XPATH.items():
            yield from self._get_follow_xpath(response, xpath, callbacks[key])

    def flat_parse(self, response):
        loader = AvitoLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in AVITO_FLAT_XPATH.items():
            loader.add_xpath(key, xpath)

        yield loader.load_item()

    # def company_parse(self, response):
    #     loader = HhEmployerLoader(response=response)
    #     for key, xpath in HH_EMPLOYER_XPATH.items():
    #         loader.add_xpath(key, xpath)
    #
    #     yield loader.load_item()