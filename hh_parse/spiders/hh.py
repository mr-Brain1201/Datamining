import scrapy

from hh_parse.loaders import HhLoader, HhEmployerLoader
from hh_parse.spiders.xpaths import HH_PAGE_XPATH, HH_VACANCY_XPATH, HH_EMPLOYER_XPATH


class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]
    start_urls = [
        "https://spb.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"
    ]

    def _get_follow_xpath(self, response, xpath, callback):
        for url in response.xpath(xpath):
            yield response.follow(url, callback=callback)

    def parse(self, response, **kwargs):
        callbacks = {"pagination": self.parse, "vacancy": self.vacancy_parse, "employer": self.company_parse}

        for key, xpath in HH_PAGE_XPATH.items():
            yield from self._get_follow_xpath(response, xpath, callbacks[key])

    def vacancy_parse(self, response):
        loader = HhLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in HH_VACANCY_XPATH.items():
            loader.add_xpath(key, xpath)

        yield loader.load_item()

    def company_parse(self, response):
        loader = HhEmployerLoader(response=response)
        for key, xpath in HH_EMPLOYER_XPATH.items():
            loader.add_xpath(key, xpath)

        yield loader.load_item()
