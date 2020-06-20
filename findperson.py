#----------------------------#
# Author: grafstor
# Date: 20.06.20
#----------------------------#

'''
helps you find a person by their profile picture
'''

__version__ = '1.0'

import parcer
import aiohttp
import asyncio

import numpy as np
from PIL import Image
from io import BytesIO

import time
import getpass

progress = 0
total = 0

get_pics = lambda persons: asyncio.run(load_pics(persons))

async def fetch_get(session, url, who):
    async with session.get(url=url) as response:
        progress_bar()
        return [Image.open(BytesIO(await response.content.read())), who]

def loader(foo):
    async def load(*items):
        async with aiohttp.ClientSession() as session:
            tasks = []
            foo(session, tasks, *items)
            return await asyncio.gather(*tasks)
    return load

@loader
def load_pics(session, tasks, persons):
    global progress, total
    progress = 0
    total = 0

    for person in persons:
        who = person['id']
        url = person['img']
        if url != '/images/camera_100.png?ava=1': 
          if url != '/images/deactivated_100.png?ava=1':
            total += 1
            tasks.append(asyncio.create_task(fetch_get(session, url, who)))

def progress_bar():
    global progress
    progress += 1

    percent = float(progress) * 100 / total
    arrow   = '▆' * int(percent/100 * 30 - 1)
    spaces  = ' ' * (30 - len(arrow))

    print(f'Getting {total} friends pics: {arrow}{spaces} {int(percent)}%', end='\r')

def mse(y_true, y_pred):
    error = np.mean(np.power(y_true - y_pred, 2))
    return error

def normalize(img):
    img.thumbnail([10, 10])
    img = np.array(img)
    img = img.reshape((300,))
    return img

def compare(img1, img2):
    try:
        img2 = normalize(img2)
    except:
        print('passed')
        return 100.0
    error = mse(img1, img2)
    return error

def find_person(tree, pic_to_search):

    pic_to_search = Image.open(pic_to_search)
    pic_to_search = normalize(pic_to_search)

    past_ids = []
    errors = []

    tree = tree[1:]

    for persons in tree:
        for i in range(len(persons)//1000+1):

            pics = get_pics(persons[i:i+1000])
            print()

            for pic in pics:
                if not pic[1] in past_ids:
                    past_ids.append(pic[1])

                    error = compare(pic_to_search, pic[0])

                    if error < 10:
                        return [error, pic[1]]

                    errors.append([error, pic[1]])

    return min(errors, key=lambda a: a[0])

def main():
    LOGIN = getpass.getpass(prompt='vk login: ')
    PASSWORD =  getpass.getpass(prompt='vk password: ')

    MIAN_ID = getpass.getpass(prompt='target id: ')
    MAIN_NAME = 'man'

    DEEP = 3

    parce_man = parcer.Tree(id=MIAN_ID,
                           name=MAIN_NAME,
                           deep=DEEP,

                           login=LOGIN,
                           password=PASSWORD)

    parce_man.start()
    tree = parce_man.get_tree()

    print(find_person(tree, 'ava.jpg'))

if __name__ == '__main__':
    main()
