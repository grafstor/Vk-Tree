# Vk Friends Tree
'''
    author: grafstor
    date: 08.04.20

    version 1.0:
        Text version

    version 2.0:
        Add images
        remove text
'''

__version__ = '2.0' 

from math import sqrt
from random import randint

from PIL import Image, ImageDraw
import requests

import parcer
import getpass

# your vk login, password to parce   python setup.py build_ext --inplace
LOGIN = getpass.getpass(prompt='vk login: ')
PASSWORD =  getpass.getpass(prompt='vk password: ')

# person to build tree
MIAN_ID = getpass.getpass(prompt='target id: ')
MAIN_NAME = 'man'

DEEP = 3

width = 3000
height = 3000

line_color = (150,150,150)
avasize = 40

def draw_circle(coords, size, color):
    x = coords[0]
    y = coords[1]
    main_img.ellipse((x-size, y-size,
                      x+size, y+size),
                      fill=color,
                      outline=color)

def draw_person(item_one, item_two, average):
    main_img.line([item_one['coord'], item_two['coord']] , fill=line_color) 

    ava = 0
    size = 0
    if item_two['img'] != '/images/camera_100.png?ava=1':
        ava = Image.open(requests.get(item_two['img'], stream=True).raw)

        resize = (item_two['coun']/average)*15
        ava.thumbnail([avasize+resize,
                       avasize+resize])
        size = avasize+resize
    else:
        size = avasize
        ava = remote_account_pic

    main_pic.paste(ava, (int(item_two['coord'][0]-size//2),
                         int(item_two['coord'][1]-size//2)))

def friends_for(action):
    def for_loop():
        for i in range(len(tree[2])):
            for j in range(len(tree[1])):
                if tree[1][j]['id'] == tree[2][i]['id']:
                    for k in range(len(tree[1])):
                        if tree[2][i]['refer'] ==  tree[1][k]['id']:
                            action(k, j)
    return for_loop

@friends_for
def correct_cords(k, j):
    tree[1][k]['coun']+=1
    x1, y1 = tree[1][j]['coord']
    x2, y2 = tree[1][k]['coord']
    lenth = sqrt((x1-x2)**2+(y1-y2)**2)
    try:
        tree[1][j]['coord'] = (x2+((x1-x2)/(lenth/200)), y2+((y1-y2)/(lenth/200)))
    except:
        pass

@friends_for
def draw_connections(k, j):
    if tree[1][j]['img'] != '/images/deactivated_100.png?ava=1':
        main_img.line([tree[1][j]['coord'], tree[1][k]['coord']], fill=(0,200,200)) 

def draw_imges():
    average_connections = sum([i['coun'] for i in tree[1]])/len(tree[1])
    for i in range(len(tree[1])):
        if tree[1][i]['img'] != '/images/deactivated_100.png?ava=1':
            draw_person(tree[0][0], tree[1][i], average_connections)








def get_remote_account_pic():
    img = requests.get('https://vk.com/images/camera_100.png?ava=1', stream=True)
    remote_account_pic = Image.open(img.raw)
    remote_account_pic.thumbnail([avasize-10,avasize-10])
    return remote_account_pic


main_pic = Image.new("RGB", (height, width))
main_img = ImageDraw.Draw(main_pic)

parce_man = parcer.Tree(id=MIAN_ID,
                           name=MAIN_NAME,
                           deep=DEEP,

                           login=LOGIN,
                           password=PASSWORD)
parce_man.start()

tree = parce_man.get_tree()

print("Load tree..")

for i in range(len(tree[1])):
    tree[1][i]['coord'] = (randint(0, width),
                           randint(0, height))
    tree[1][i]['coun'] = 0

tree[0][0]['coord'] = (width//2,
                       height//2)

remote_account_pic = get_remote_account_pic()



correct_cords()
draw_connections()
draw_imges()

draw_circle(tree[0][0]['coord'], 10, (255,255,255))

print('Done')

main_pic.save('result.png', "PNG")
main_pic.show()
