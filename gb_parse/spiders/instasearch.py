import scrapy
import json
import pickle
import sys
from urllib.parse import urlencode  # , parse_qs, urljoin
from gb_parse.items import InstaItem


# import datetime as dt


class InstasearchSpider(scrapy.Spider):
    name = 'instasearch'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'

    query_hash = {
        'following': 'd04b0a864b4b54837c0d870b0e77e076',
        'followers': 'c76146de99bb02f6415203be841dd25a'
    }

    url_api = 'https://www.instagram.com/graphql/query/'
    variables = {"id": '',
                 'include_reel': 'true',
                 'fetch_mutual': 'false',
                 'first': 100,
                 'after': ''
                 }
    list_id = []
    db = {}
    work_graph = []
    graph = {
        'target_user': [],
        'chance_to_way': False,
        'way_list': [],
        'data': {
            '1': {'all': set(), },
            '2': {'all': set(), }
        }
    }

    def __init__(self, login, password, accounts_list, file, *args, **kwargs):
        self.login = login
        self.file = file
        self.password = password
        self.accounts_list = accounts_list
        super(InstasearchSpider, self).__init__(*args, **kwargs)
        self.graph['target_user'].append(accounts_list[0])
        self.graph['target_user'].append(accounts_list[1])

    def parse(self, response, **kwargs):
        username = None
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError as err:
            print(err)
            if response.json().get('authenticated'):
                if len(self.list_id) == 0:
                    for i, account in enumerate(self.accounts_list):
                        self.list_id.append(account)
                        yield response.follow(f'/{account}/', callback=self.get_graph, meta={'side': str(i + 1)})
                else:
                    self.list_id.append(username)
                    return response.follow(f'/{username}/', callback=self.get_graph)

    def get_graph(self, response):  # функция входа, через которую проходт только стартовые аккаунты
        js_data = self.js_data_extract(response)
        side = response.meta['side']
        js_data_user = js_data['entry_data']['ProfilePage'][0]['graphql']['user']
        id = js_data_user['id']
        username = js_data_user['username']
        self.list_id.append(username)
        self.graph['data'][side]['all'].add(id)
        for hash in self.query_hash.keys():
            url_api = self.get_api_url(id, hash)
            yield response.follow(
                url_api,
                callback=self.parse_api,
                meta={'follow': hash,
                      'id': id,
                      'side': side,
                      }
            )

    def parse_api(self, response):
        follow = response.meta['follow']
        id = response.meta['id']
        side = response.meta['side']
        data = json.loads(response.body)

        # если нет в графе в строках или есть, но с нулевой длиной, заполняем сначала db (временные данные с парсинга)
        if (id not in self.graph['data'][side]) or (not len(self.graph['data'][side][id])):
            if id not in self.db:  # добавляем в оперативную базу db
                self.db[id] = {
                    'side': side,
                    'followers': [],
                    'following': []
                }
            if follow == 'followers':
                data = data['data']['user']['edge_followed_by']
                for edge in data["edges"]:
                    self.list_id.append(edge["node"]["username"])
                self.db[id]['count_followers'] = data['count']
            else:
                data = data['data']['user']['edge_follow']
                for edge in data["edges"]:
                    self.list_id.append(edge["node"]["username"])
                self.db[id]['count_following'] = data['count']

            # добавляем списки подписантов или подписчиков
            for pack_follow in self.parse_followers(data):
                self.db[id][follow].append(pack_follow)

            # сканируем следующие страницы с api
            # while data['page_info']['has_next_page']:
            #     after = data['page_info']['end_cursor']
            #     url_api = self.get_api_url(id, follow, after)
            #     yield response.follow(
            #         url_api,
            #         callback=self.parse_api,
            #         meta={'follow': follow, 'id': id, 'side': side}
            #     )

            # если количество собранных аккаунтов в обеих списках полное, отправляем в pipeline item взаимные
            if ('count_followers' in self.db[id]) and ('count_following' in self.db[id]):
                if (len(self.db[id]['followers']) == self.db[id]['count_followers']) and (
                        len(self.db[id]['following']) == self.db[id]['count_following']):
                    f1 = set(self.db[id]['followers'])
                    f2 = set(self.db[id]['following'])
                    mutual_follower = f2.intersection(f1)  # убираем не взаимные
                    self.work_graph.append(mutual_follower)
                    for follower in mutual_follower:
                        str(follower)
                        return mutual_follower
                    print(1)
                    # self.list_id.
                    data_pipeline = {
                        'side': self.db[id]['side'],
                        'id': id,
                        'graph': mutual_follower,
                        'list_name': set(self.list_id),
                        'work_graph': self.work_graph,
                        'target_user': self.accounts_list[1]
                    }
                    item = InstaItem(data_pipeline)
                    del self.db[id]

                    yield response.follow(f'/{data["edges"]["node"]["username"]}/', callback=self.get_graph)
                    return item

        # вывод текущей информации о размере основного графа
        print(len(self.graph['data']['1']), len(self.graph['data']['2']))
        print(sum([len(x) for x in self.graph['data']['1']]), sum([len(x) for x in self.graph['data']['2']]))

        # считываем id из секции all и добавляем как пустые множества для дальнейшего наполнения взаимными id
        temp_graph = self.graph['data'].copy()
        for side, list in temp_graph.items():
            for id in list['all']:
                if id not in self.graph['data'][side]:
                    self.graph['data'][side][id] = set()
                    for hash in self.query_hash.keys():
                        url_api = self.get_api_url(id, hash)
                        yield response.follow(
                            url_api,
                            callback=self.parse_api,
                            meta={'follow': hash, 'id': id, 'side': side}
                        )

    # функция формирования ссылки для api
    def get_api_url(self, id, follow, after=''):
        loc_variables = self.variables.copy()
        loc_variables['id'] = id
        loc_variables['after'] = after
        base_params = {
            'query_hash': self.query_hash[follow],
            'variables': json.dumps(loc_variables)
        }
        return f'{self.url_api}?{urlencode(base_params)}'

    @staticmethod
    def parse_followers(data):
        for user in data['edges']:
            yield user['node']['id']

    def js_data_extract(self, response):
        script = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        return json.loads(script.replace("window._sharedData = ", '')[:-1])
