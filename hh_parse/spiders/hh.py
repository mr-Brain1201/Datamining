import scrapy

from hh_parse.loaders import HhLoader, HhEmployerLoader
from hh_parse.spiders.xpaths import HH_PAGE_XPATH, HH_VACANCY_XPATH, HH_EMPLOYER_XPATH, HH_EMPLOYER_VACANCY_XPATH


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
        callbacks = {"pagination": self.parse, "vacancy": self.vacancy_parse, "employer": self.company_parse,
                     "vacancy_employer": self._get_employer_vacancies}

        for key, xpath in HH_PAGE_XPATH.items():
            yield from self._get_follow_xpath(response, xpath, callbacks[key])

    def vacancy_parse(self, response):
        loader = HhLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in HH_VACANCY_XPATH.items():
            loader.add_xpath(key, xpath)

        yield loader.load_item()

    def company_parse(self, response):
        yield from self._get_employer_vacancies(response=response)
        loader = HhEmployerLoader(response=response)
        for key, xpath in HH_EMPLOYER_XPATH.items():
            loader.add_xpath(key, xpath)

        yield loader.load_item()

    def _get_employer_id(self, response):
        id = response._get_url()[-7:]
        return id

    def _get_employer_vacancies(self, response):
        prof_area = [i for i in range(1, 30)]
        id = self._get_employer_id(response=response)
        for area in prof_area:
            page = 0
            region_list = ['CURRENT', 'OTHER']
            for region in region_list:
                if len(response.xpath('//body/span')) > 0:
                    while len(response.xpath('//body/span')) > 0:
                        url = f'https://spb.hh.ru/shards/employerview/vacancies?page={page}&profArea={area}\
                                    &currentEmployerId={id}&regionType={region}'
                        page += 1
                        yield response.follow(url)
                else:
                    url = f'https://spb.hh.ru/shards/employerview/vacancies?page={page}&profArea={area}\
                                                        &currentEmployerId={id}&regionType={region}'
                    yield response.follow(url)



