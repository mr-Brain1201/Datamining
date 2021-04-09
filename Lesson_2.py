import requests
from urllib.parse import urljoin
import datetime as dt
import time
import bs4
import pymongo
from urllib3.exceptions import NewConnectionError, MaxRetryError

MONTHS = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12
}


class MagnitParse:
    headers = {"User-Agent": "cap. Jack Sparrow"}

    def __init__(self, start_url, db_client):
        self.start_url = start_url
        db = db_client["gb_data_mining"]
        self.collection = db["magnit"]

    def _get_response(self, url, *args, **kwargs):
        while True:
            response = requests.get(url, *args, **kwargs, headers=self.headers)
            if response.status_code in (200, 301, 304):
                return response
            time.sleep(1)

    def _get_soup(self, url, *args, **kwargs):
        return bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")

    def run(self):
        while True:
            try:
                for product in self._parse(self.start_url):
                    self._save(product)
            except ValueError as err:
                print(err)
                break
            except (NewConnectionError, MaxRetryError,
                    requests.exceptions.ConnectionError) as connect_err:
                print(connect_err)
                time.sleep(10)
            else:
                break

    @property
    def _template(self):
        return {
            "url": lambda tag: urljoin(self.start_url, tag.attrs.get("href", "")),
            "promo_name": lambda tag: tag.find("div", attrs={"class": "card-sale__name"}).text,
            "product_name": lambda tag: tag.find("div", attrs={"class": "card-sale__title"}).text,
            "old_price": lambda tag: float(
                ".".join(
                    itm for itm in tag.find("div", attrs={"class": "label__price_old"}).text.split()
                )
            ),
            "new_price": lambda tag: float(
                ".".join(
                    itm for itm in tag.find("div", attrs={"class": "label__price_new"}).text.split()
                )
            ),
            "image_url": lambda tag: urljoin(self.start_url, tag.find("img").attrs.get("data-src")),
            "data_from": lambda tag: self.__get_date(
                tag.find("div", attrs={"class": "card-sale__date"}).text
            )[0],
            "data_to": lambda tag: self.__get_date(
                tag.find("div", attrs={"class": "card-sale__date"}).text
            )[1]
        }
    def __get_date(self, date_string) -> list:
        global temp_year
        date_list = date_string.replace("с ", "", 1).replace("\n", "").split("до")
        result = []
        for date in date_list:
            temp_date = date.split()
            temp_month = MONTHS.get(temp_date[1][:3])
            if temp_month != 1 or 12:
                temp_year = dt.datetime.now().year
            elif dt.datetime.now().month == 1 and temp_month == 12:
                temp_year = dt.datetime.now().year - 1
            elif dt.datetime.now().month == 12 and temp_month == 1:
                temp_year = dt.datetime.now().year + 1
            result.append(
                dt.datetime(
                    year=temp_year,
                    day=int(temp_date[0]),
                    month=MONTHS.get(temp_date[1][:3])
                )
            )
        return result

    def _parse(self, url):
        soup = self._get_soup(url)
        catalog_main = soup.find("div", attrs={"class": "сatalogue__main"})
        product_tags = catalog_main.find_all("a", recursive=False)
        for product_tag in product_tags:
            product = {}
            for key, funk in self._template.items():
                try:
                    product[key] = funk(product_tag)
                except (AttributeError, IndexError, ValueError):
                    product[key] = None
            yield product

    def _save(self, data):
        self.collection.insert_one(data)


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = MagnitParse(url, db_client)
    parser.run()
