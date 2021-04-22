
import re
from urllib.parse import urljoin

from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


def replace_text(items):
    return items.replace('\xa0', ' ')


def avito_seller_url(user_id):
    return urljoin("https://avito.ru/", user_id)
#
#
# def hh_employer_title(title):
#     return title.replace("Работа в компании ", "").partition(".")[0]
#
#
# def hh_employer_area(area):
#     return area.split(", ")


def get_price(text):
    re_pattern = re.compile(r'"dynx_price":(\d+)')
    result = re.findall(re_pattern, text)
    return result


class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = MapCompose(replace_text)
    title_out = TakeFirst()
    price_in = MapCompose(get_price)
    price_out = TakeFirst()
    address_out = TakeFirst()
    # params_out = TakeFirst()
    seller_url_in = MapCompose(avito_seller_url)
    seller_url_out = TakeFirst()
    # salary_out = flat_text
    # description_in = flat_text,
    # description_out = flat_text,
    # author_in = MapCompose(hh_user_url)
    # author_out = TakeFirst()