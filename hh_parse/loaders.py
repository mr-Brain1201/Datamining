
import re
from urllib.parse import urljoin

from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


def flat_text(items):
    return "\n".join(items).replace('\n', '')


def hh_user_url(user_id):
    return urljoin("https://hh.ru/", user_id)


def hh_employer_title(title):
    return title.replace("Работа в компании ", "").partition(".")[0]


def hh_employer_area(area):
    return area.split(", ")


class HhLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = flat_text
    # description_in = flat_text,
    # description_out = flat_text,
    author_in = MapCompose(hh_user_url)
    author_out = TakeFirst()


class HhEmployerLoader(ItemLoader):
    default_item_class = dict
    title_in = MapCompose(hh_employer_title)
    title_out = TakeFirst()
    url_out = TakeFirst()
    area_in = MapCompose(hh_employer_area)
    # description_in = flat_text,
    # description_out = flat_text,
