import requests
import bs4
from urllib.parse import urljoin
from database.database import Database
import datetime as dt
from time import sleep
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


class GbBlogParse:
    headers = {"User-Agent": "cap. Jack Sparrow"}

    def __init__(self, start_url, database: Database):
        self.db = database
        self.start_url = start_url
        self.done_urls = set()
        self.tasks = [
            self.get_task(self.start_url, self.parse_feed),
        ]
        self.done_urls.add(self.start_url)

    def get_task(self, url, callback):
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        return task

    def _get_response(self, url, *args, **kwargs) -> requests.Response:
        while True:
            response = requests.get(url, *args, **kwargs, headers=self.headers)
            if response.status_code in (200, 301, 304):
                return response
            sleep(1)

    def _get_soup(self, url):
        soup = bs4.BeautifulSoup(self._get_response(url).text, "lxml")
        return soup

    def parse_post(self, url, soup):
        author_tag = soup.find("div", attrs={"itemprop": "author"})
        data = {
            "post_data": {
                "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                "url": url,
                "id": soup.find("comments").attrs.get("commentable-id"),
                "date": self.__get_date(soup.find(
                    "time",
                    attrs={
                        "class": "text-md text-muted m-r-md",
                        "itemprop": "datePublished"
                    }
                ).text),
                "image_url": soup.find("div", attrs={"class": "blogpost-content"}).find("img").attrs.get("src")
            },
            "writer_data": {
                "url": urljoin(url, author_tag.parent.attrs.get("href")),
                "name": author_tag.text,
            },
            "tags_data": [
                {"name": tag.text, "url": urljoin(url, tag.attrs.get("href"))}
                for tag in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments_data": self._get_comments(soup.find("comments").attrs.get("commentable-id")),
        }
        return data

    def __get_date(self, date_string):
        temp_date = date_string.split()
        date_post = dt.datetime(
            year=int(temp_date[-1]),
            day=int(temp_date[0]),
            month=MONTHS.get(temp_date[1][:3])
        )
        return date_post

    def _get_comments(self, post_id):
        api_path = f"/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc"
        response = self._get_response(urljoin(self.start_url, api_path))
        data = response.json()
        return data

    def parse_feed(self, url, soup):
        ul = soup.find("ul", attrs={"class": "gb__pagination"})
        pag_urls = set(
            urljoin(url, href.attrs.get("href"))
            for href in ul.find_all("a")
            if href.attrs.get("href")
        )
        for pag_url in pag_urls:
            if pag_url not in self.done_urls:
                self.tasks.append(self.get_task(pag_url, self.parse_feed))

        post_items = soup.find("div", attrs={"class": "post-items-wrapper"})
        posts_urls = set(
            urljoin(url, href.attrs.get("href"))
            for href in post_items.find_all("a", attrs={"class": "post-item__title"})
            if href.attrs.get("href")
        )

        for post_url in posts_urls:
            if post_url not in self.done_urls:
                self.tasks.append(self.get_task(post_url, self.parse_post))

    def run(self):
        while True:
            try:
                for task in self.tasks:
                    task_result = task()
                    if task_result:
                        self.db.create_post(task_result)
            except ValueError as err:
                print(err)
                break
            except (NewConnectionError, MaxRetryError,
                    requests.exceptions.ConnectionError) as connect_err:
                print(connect_err)
                sleep(10)
            else:
                break

    def save(self, data):
        self.db.create_post(data)


if __name__ == "__main__":
    database = Database("sqlite:///gb_blog.db")
    parser = GbBlogParse("https://gb.ru/posts", database)
    parser.run()
