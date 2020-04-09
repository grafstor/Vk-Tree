# Vk Friends Tree
'''
    author: grafstor
    date: 01.04.20

    version 1.0:
        Return matrix of dict:
            {id,name,refers,img}
'''

__version__ = "1.0"

import requests
import lxml.html
import asyncio
import time

class Manager:
    def __init__(self, id=1, name='you', deep=2, login=0, password=0):
        '''parce builder'''
        self.parcer = Parcer(id, name, deep, login, password)
        self.tree = []

    def __start(self):
        '''call parcer'''
        self.parcer.start()

    def build_tree(self):
        '''start main loop'''
        self.__start()
        self.tree = self.parcer.get_tree()

    def get_tree(self):
        '''after building return friends tree'''
        return self.tree


class Informer:
    def __init__(self):
        self.tt = 0.0
        self.toggle = False

    def log(self, text, num=0):
        if self.toggle:
            print(f'{text}',end='  ')
            print(f'ranning time: {time.time()-self.tt}')
            self.toggle = False
        else:
            print(f'{text}: {num}')
            self.tt = time.time()
            self.toggle = True


class Parcer:
    def __init__(self, id, name, deep, login, password):
        self.inf = Informer()
        self.session = self.__start_session(login,
                                            password)
        
        page = self.session.get('https://vk.com/feed').text
        page = page[page.find('href="/albums')+13:]
        self.main_id = int(page[:page.find('"')])

        self.deep = deep
        self.id = id
        self.name = name

        self.to_check = self.__convert(self.__get_pages([self.main_id])[0])
        self.tree = [[] for i in range(deep)]

    def start(self):
        self.__tree(self.deep,
                    [{'id':self.id,
                      'name':self.name,
                      'refer':''}])
        print('Parsing done!')
        print(f'Total persons: {sum([len(i) for i in self.tree])}')

    def __tree(self, iteration, persons):
        '''get iteration and array 
            with {id, name, refers}'''
        self.tree[self.deep - iteration].extend(persons)

        if iteration <= 1:
            return

        ids = [person["id"] for person in persons]

        self.inf.log('Requests', len(ids))
        pages = self.__get_pages(ids)
        self.inf.log('Requests')

        friends_of_persons = [self.__convert(page) for page in pages]

        for i in range(len(friends_of_persons)):
            if self.__is_closed(friends_of_persons[i], persons[0]['id']):
                continue
            friends = friends_of_persons[i]

            for j in range(len(friends)):
                friends[j]['refer'] = persons[i]['id']
                # friends[j]['iter'] = self.deep - iteration + 1

            self.__tree(iteration-1, friends)

    def __convert(self, page):
        page = page.replace("\\", "")[28:]
        info_list = []

        while True:
            left_border = page.find("[")
            if left_border == -1:break
            page = page[left_border:]

            right_border = page.find(']')
            info_list.append(page[:right_border])
            page = page[right_border:]

        for i in range(len(info_list)):
            if '[[' in info_list[i]:
                info_list = info_list[:i]
                break

        convert_info_list = []
        for person in info_list:
            person = person[1:].split(",")
            id = person[0][1:-1]

            try:
                if '<span'in person[5]:
                    right_border = person[5].find("<span")
                    person[5] = person[5][:right_border]
                man = person[5][1:-1]
                image = person[1][1:-1]
            except:
                man = "-noname-"
            convert_info_list.append({"id": id,
                                      "name": man,
                                      "refer": [],
                                      "img": image})
        return convert_info_list

    async def __fast_requests(self, ids):
        pages = []
        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(None, lambda: 
                    self.session.post("https://vk.com/al_friends.php",
                        data={'act': 'load_friends_silent',
                              'id': str(id),
                              'al': '1',
                              'gid': '0',})) for id in ids]
        for response in await asyncio.gather(*futures):
            pages.append(response.text)
        return pages

    def __get_pages(self, ids):
        loop = asyncio.get_event_loop()
        pages = loop.run_until_complete(self.__fast_requests(ids))
        return pages

    def __start_session(self, login, password):
        url = 'https://vk.com/'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                              (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
                    'Accept-Encoding':'gzip, deflate',
                    'Connection':'keep-alive',
                    'cookie':'remixscreen_height=20000;remixscreen_depth=100;remixscreen_winzoom=0.2;',
                    'DNT':'1'}

        session = requests.session()
        data = session.get(url, headers=headers)
        page = lxml.html.fromstring(data.content)

        form = page.forms[0]
        form.fields['email'] = login
        form.fields['pass'] = password
          
        session.post(form.action, data=form.form_values())
        return session

    def __is_closed(self, friends, first):
        if len(friends) == 9:
            if self.to_check[1]['id'] == friends[1]["id"]:
                if first != self.main_id:
                    return True
        return False

    def get_tree(self):
        return self.tree
