# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo


class HhParsePipeline:
    def process_item(self, item, spider):
        return item


class HhParseMongoPipeline:
    def __init__(self):
        client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = client["hh_parse"]

    def process_item(self, item, spider):
        if "area" in item.keys():
            self.db[spider.name + "_employers"].insert_one(item)
        else:
            self.db[spider.name].insert_one(item)
        return item
