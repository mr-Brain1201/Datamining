# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
# from itemloaders.processors import Identity


class InstaItem(scrapy.Item):
    side = scrapy.Field()
    id = scrapy.Field()
    graph = scrapy.Field()
    list_name = scrapy.Field()
    work_graph = scrapy.Field()
    target_user = scrapy.Field()
