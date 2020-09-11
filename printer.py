#-------------------------------#
#       Author: grafstor        
#       Date: 08.04.20          
#-------------------------------#

import sys
import traceback

from math import sqrt
from random import randint

import requests
from PIL import Image, ImageDraw

from vktree import *

# your vk login, password to parce
LOGIN = sys.argv[1]
PASSWORD =  sys.argv[2]

# person to build tree
MIAN_ID = sys.argv[3]
MAIN_NAME = 'man'

DEEP = 2

def friends_for(action):
    def for_loop(self, tree):
        for i in range(len(tree[1])):
            for j in range(len(tree[0])):
                if tree[0][j]['id'] == tree[1][i]['id']:
                    for k in range(len(tree[0])):
                        if tree[1][i]['refers'] ==  tree[0][k]['id']:
                            action(self, k, j)
    return for_loop

class Drawer:
    def __init__(self):
        self.width = 3000
        self.height = 3000

        self.line_color = (150, 150, 150)
        self.avasize = 40

        self.center = (self.width//2,
                       self.height//2)

        self.main_pic = Image.new("RGB", (self.height, self.width))
        self.main_img = ImageDraw.Draw(self.main_pic)

        self.remote_account_pic = self.get_remote_account_pic()

    def load(self, tree):
        for i in range(len(tree[0])):
            tree[0][i]['coord'] = (randint(0, self.width),
                                   randint(0, self.height))
            tree[0][i]['coun'] = 0

        self.tree = tree

        self.correct_cords(self.tree)
        self.draw_connections(self.tree)
        self.draw_imges()

        self.draw_circle(self.center, 10, (255,255,255))

        self.main_pic.save('result.png', "PNG")

    @friends_for
    def correct_cords(self, k, j):
        self.tree[0][k]['coun']+=1
        x1, y1 = self.tree[0][j]['coord']
        x2, y2 = self.tree[0][k]['coord']
        lenth = sqrt((x1-x2)**2+(y1-y2)**2)
        try:
            self.tree[0][j]['coord'] = (x2+((x1-x2)/(lenth/200)), y2+((y1-y2)/(lenth/200)))
        except:
            pass

    @friends_for
    def draw_connections(self, k, j):
        if self.tree[0][j]['img'] != '/images/deactivated_100.png?ava=1':
            self.main_img.line([self.tree[0][j]['coord'], self.tree[0][k]['coord']], fill=(0,200,200)) 

    def draw_imges(self):
        average_connections = sum([i['coun'] for i in self.tree[0]])/len(self.tree[0])

        for i in range(len(self.tree[0])):
            if self.tree[0][i]['img'] != '/images/deactivated_100.png?ava=1':
                self.draw_person(self.center, self.tree[0][i], average_connections)

    def draw_person(self, item_one, item_two, average):
        self.main_img.line([item_one, item_two['coord']] , fill=self.line_color) 

        size = self.avasize
        ava = self.remote_account_pic
        
        if item_two['img'] != '/images/camera_100.png?ava=1':
            try:
                ava = Image.open(requests.get(item_two['img'], stream=True).raw)
                # ava.show()

                resize = (item_two['coun']/average)*15
                ava.thumbnail([self.avasize+resize,
                               self.avasize+resize])
                size = self.avasize+resize

            except:
                pass

        self.main_pic.paste(ava, (int(item_two['coord'][0]-size//2),
                                  int(item_two['coord'][1]-size//2)))


    def draw_circle(self, coords, size, color):
        x = coords[0]
        y = coords[1]
        self.main_img.ellipse((x-size, y-size,
                              x+size, y+size),
                              fill=color,
                              outline=color)

    def get_remote_account_pic(self):
        img = requests.get('https://vk.com/images/camera_100.png?ava=1', stream=True)
        remote_account_pic = Image.open(img.raw)
        remote_account_pic.thumbnail([self.avasize-10,self.avasize-10])
        return remote_account_pic

def main():
    parcer = Parcer(login=LOGIN, password=PASSWORD)
    tree = parcer.download_tree(MIAN_ID, DEEP)

    print("Load picture..")
    drawer = Drawer()
    drawer.load(tree)

    print('Done')


if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print('exit')

    except:
        traceback.print_exc(limit=-1, file=sys.stdout)
