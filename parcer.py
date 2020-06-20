# Vk Friends Tree
'''
    author: grafstor
    date: 01.04.20

    version 1.0:
        Return matrix of dict:
            {id, name, refers, img}

    version 2.0:
        From requests to aiohttp
        progress bar

    version 2.1:
        bag fix
        refactoring
'''

__version__ = "2.1"

import aiohttp
import lxml.html
import asyncio

url_to_session = 'https://vk.com/'
url_to_friends = 'https://vk.com/al_friends.php'

headers_to_session = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
        'Accept-Encoding':'gzip, deflate',
        'Connection':'keep-alive',
        'DNT':'1'
    }

data_to_friends = {
        'act': 'load_friends_silent',
        'id': '{}',
        'al': '1',
        'gid': '0',
    }

class Tree:
    def __init__(self, id, name, deep, login, password):
        self.login = login
        self.password = password

        self.main_id = self.__get_main_id()

        self.deep = deep
        self.id = id
        self.name = name

        self.progress = 0
        self.progress_len = 0

        self.self_info = self.__get_friends([self.main_id])[0]
        self.tree = [[] for i in range(deep)]

    def start(self):
        self.__tree(self.deep,
                    [{'id': self.id,
                      'name': self.name,
                      'refer': ''}])
        print('Parsing done!')
        print(f'Total persons: {sum([len(i) for i in self.tree])}')

    def get_tree(self):
        return self.tree

    def __tree(self, iteration, persons):
        self.tree[self.deep - iteration].extend(persons)
        
        if iteration <= 1:
            return

        ids = [person["id"] for person in persons]

        friends_of_persons = self.__get_friends(ids)
        print()

        for i in range(len(friends_of_persons)):
            if self.__is_closed(friends_of_persons[i], persons[0]['id']):
                continue

            friends = friends_of_persons[i]

            for j in range(len(friends)):
                friends[j]['refer'] = persons[i]['id']

            self.__tree(iteration-1, friends)

    def __get_friends(self, ids):
        friends = asyncio.run(self.__load_friends(ids, self.__convert))
        return friends

    async def __fetch_post(self, session, url, data, convert):
        async with session.post(url=url, data=data) as response:
            self.__progress_bar()
            return convert(await response.text())

    async def __load_friends(self, ids, convert, auth=True):
        async with aiohttp.ClientSession() as session:
            if auth:
                async with session.get(url=url_to_session, headers=headers_to_session) as data:
                    page = lxml.html.fromstring(await data.text())
                    form = page.forms[0]
                    form.fields['email'] = self.login
                    form.fields['pass'] = self.password
                async with session.post(form.action, data=form.form_values()) as _: pass

            tasks = []
            url = url_to_friends

            self.progress = 0
            self.progress_len = len(ids)

            for post in enumerate(ids):
                data = data_to_friends.copy()
                data['id'] = post
                tasks.append(asyncio.create_task(self.__fetch_post(session, url, data, convert)))

            return await asyncio.gather(*tasks)

    async def __get_main_id(self):
        async with aiohttp.ClientSession() as session:
            
            async with session.get(url=url_to_session, headers=headers_to_session) as data:
                page = lxml.html.fromstring(await data.text())
                form = page.forms[0]
                form.fields['email'] = self.login
                form.fields['pass'] = self.password
            async with session.post(form.action, data=form.form_values()) as _: pass

            async with session.get(url='https://vk.com/feed') as data:
                page = data.text()
                page = page[page.find('href="/albums')+13:]
                id = int(page[:page.find('"')])
                return id

    def __convert(self, page):
        page = page.replace("\\", "")[28:]

        persons_info_list = self.__split_page(page)

        convert_info_list = self.__normalize_infos(persons_info_list)

        return convert_info_list

    def __split_page(self, page):
        persons_info_list = []

        while True:
            left_border = page.find("[")
            if left_border == -1:
                break
            page = page[left_border:]

            right_border = page.find(']')
            persons_info_list.append(page[:right_border])
            page = page[right_border:]

        for i in range(len(persons_info_list)):
            if '[[' in persons_info_list[i]:
                persons_info_list = persons_info_list[:i]
                break

        return persons_info_list

    def __normalize_infos(self, persons_info_list):
        convert_info_list = []

        for person_info in persons_info_list:
            person_info = person_info[1:].split(",")
            id = person_info[0][1:-1]

            try:
                if '<span'in person_info[5]:
                    right_border = person_info[5].find("<span")
                    person_info[5] = person_info[5][:right_border]

                man = person_info[5][1:-1]
                image = person_info[1][1:-1]

            except:
                man = "-noname-"
            convert_info_list.append({"id": id,
                                      "name": man,
                                      "refer": [],
                                      "img": image})

        return convert_info_list

    def __progress_bar(self):
        self.progress += 1

        percent = float(self.progress) * 100 / self.progress_len
        arrow   = '▆' * int(percent/100 * 30 - 1)
        spaces  = ' ' * (30 - len(arrow))

        print(f'Getting {self.progress_len} friends packs: {arrow}{spaces} {int(percent)}%', end='\r')

    def __is_closed(self, friends, first):
        if len(friends) == 9:
            if self.self_info[1]['id'] == friends[1]["id"]:
                if int(first) != self.main_id:
                    return True
        return False
