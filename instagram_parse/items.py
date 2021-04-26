# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagParseItem(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    images = scrapy.Field()
#
# class Insta(scrapy.Item):
#     _id = scrapy.Field()
#     date_parse = scrapy.Field()
#     data = scrapy.Field()
#     # photos = scrapy.Field()


class InstagTag(InstagParseItem):
    pass


class InstagPost(InstagParseItem):
    pass