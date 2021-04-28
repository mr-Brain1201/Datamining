import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
# import time
from gb_parse.spiders.instasearch import InstasearchSpider

import dotenv

# from gb_parse import settings
dotenv.load_dotenv('.env')
accounts_list = ['_thomas_brain_', 'willow_ci']
file = 'graph.txt'

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')

    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(InstasearchSpider,
                     login=os.getenv('USRN'),
                     password=os.getenv('ENC_PASSWORD'),
                     accounts_list=accounts_list,
                     file=file)
    crawl_proc.start()
    print(1)
    #time.sleep(20)
    #crawl_proc._signal_shutdown(9,0) #Run this if the cnxn fails.