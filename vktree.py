#-------------------------------#
#       Author: grafstor        
#       Date: 11.08.20          
#-------------------------------#

import os
import aiohttp
import asyncio

import lxml.html
import numpy as np

from urls import *


class Parcer:
    def __init__(self, login, password):
        self.login = login
        self.password = password

        self.progress = 0
        self.progress_len = 0

        self.root_info = None

        self.directory = 'data/'

    def download_tree(self, id, deep):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        try:
            tree = self.__load_tree(id, deep)
            print('Tree load!')

        except:
            root_id = {'id':self.__get_main_id()}
            self.root_info = self.__get_packs([root_id])[0]

            root = [{'id': id,
                     'name': 'root',
                     'refers': None}]

            tree = self.__tree(deep, root)

            print('\nParsing done!')
            print(f'Total persons: {sum([len(i) for i in tree])}')

            self.__save_tree(id, deep, tree)
            print('Tree saved!')

        return tree

    def __load_tree(self, id, deep):
        tree_name = f'{id}-{deep}'
        tree = np.load(f'{self.directory}{tree_name}.npy', allow_pickle=True)
        return tree

    def __save_tree(self, id, deep, tree):
        tree_name = f'{id}-{deep}'
        tree = np.array(tree)
        np.save(self.directory + tree_name, tree)

    def __tree(self, deep, root):
        tree = [[] for i in range(deep)]
        
        root_friends = self.__get_packs(root)[0]
        pack = {'friends': root_friends, 'live': 1}

        stack = [pack]

        while len(stack) > 0:
            pack = stack.pop(0)

            tree[pack['live']-1].extend(pack['friends'])

            if pack['live'] != deep:

                friends_packs = self.__get_packs(pack['friends'])
                packs = self.__split_friends_packs(friends_packs, pack['live'])

                stack.extend(packs)

            else:
                pass

        return tree

    def __split_friends_packs(self, packs, live):
        batch_size = 100

        big_pack = []
        new_packs = []

        for pack in packs:
            for person in pack:
                big_pack.append(person)

        num = int(len(big_pack)/batch_size+1)

        for i in range(num):
            pack = big_pack[i*batch_size : (i+1)*batch_size]
            pack = {'friends': pack, 'live': live+1}
            new_packs.append(pack)

        return new_packs

    def __get_packs(self, pack):
        ids = [person['id'] for person in pack]
        try:
            friends = asyncio.run(self.__load_friends(ids, self.__convert))
        
        except Exception as E:
            print('Error with load pack')

        return friends

    async def __fetch_post(self, session, url, data, convert):
        async with session.post(url=url, data=data) as response:
            self.__progress_bar()
            return convert(await response.text(), data['id'][1])

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

    def __convert(self, *data):

        page, refer = data

        page = page.replace("\\", "")[28:]

        persons_info_list = self.__split_page(page)

        convert_info_list = self.__normalize_infos(persons_info_list, refer)

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

    def __normalize_infos(self, persons_info_list, refer):
        convert_info_list = []

        for person_info in persons_info_list:
            person_info = person_info[1:].split('","')

            id = person_info[0][1:]

            try:
                if '<span'in person_info[5]:
                    right_border = person_info[5].find("<span")
                    person_info[5] = person_info[5][:right_border]

                name = person_info[5]
                url = person_info[2][1:]
                image = person_info[1]

            except:
                name = "-noname-"
                url = "-nourl-"

            convert_info_list.append({"id": id,
                                      "name": name,
                                      "url": url,
                                      "refers": refer,
                                      "img": image})

        return convert_info_list

    def __is_closed(self, friends, first):
        if self.root_info[1]['id'] == friends[1]["id"]:
            if int(first) != self.main_id:
                return True
        return False

    def __progress_bar(self):
        self.progress += 1

        percent = float(self.progress) * 100 / self.progress_len
        arrow   = '▆' * int(percent/100 * 30 - 1)
        spaces  = ' ' * (30 - len(arrow))

        print(f'Getting {self.progress_len} friends packs: {arrow}{spaces} {int(percent)}%', end='\r')

def print_tree(tree, key=-1):
    if key == -1:
        for deep in tree:
            for j, person in enumerate(deep):
                print(j, person['id'], person['name'], person['url'], person['refers'], person['img'])
    else:
        for j, person in enumerate(tree[key]):
            print(j, person['id'], person['name'], person['url'], person['refers'], person['img'])

def len_tree(tree):
    for i, deep in enumerate(tree):
        print('deep', i+1, len(deep))
