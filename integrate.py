from PIL import Image, ImageFilter
import os
import datetime
import io

length = 128

#一次元イメージ配列の入力から、配列に入った画像をx軸正方向に連結させた画像を作る
def getx(image_list):
    dst =  Image.new('RGBA', (length*len(image_list), image_list[0].height))
    pos_x = 0
    for im in image_list:
        dst.paste(im, (pos_x,0))
        pos_x += length
    return dst

#一次元イメージ配列の入力から、配列に入った画像をy軸正方向に連結させた画像を作る
def gety(image_list):
    dst = Image.new('RGBA', (image_list[0].width, length*len(image_list)))
    pos_x = length*(len(image_list)-1)
    for im in image_list:
        dst.paste(im, (0,pos_x))
        pos_x -= length
    return dst

#二次元イメージ配列の入力からタイル状に連結した画像を作る
def integrate(image_list_2d):
    temp_im_x = [getx(im) for im in image_list_2d]
    return gety(temp_im_x)

#二次元イメージ配列を作る。入力は左下と右上の地図座標。
def mkimlist2d(x0,y0,x1,y1):
    image_list_2d =[]
    for i in range(y0,y1+1):
        a = './latest_128/0,{0},{1}.png'
        image_list_x =[
            Image.open(a.format(j,i))
            if os.path.exists(a.format(j,i))
            else Image.new('RGBA',(length,length))
            for j in range(x0,x1+1)
        ]
        image_list_2d.append(image_list_x)
    return image_list_2d

ic = [0,3,4,5]
sh = [0,-1,3,1]
cc = [-4,1,0,4]
hm = [1,-5,5,-4]
si = [-6,0,-4,2]
ph = [-10,2,-5,7]
si = [-3,-4,0,0]
br = [-7,7,-4,10]
all = [-10,-10,16,14]

def integrate_go(area):
    #以下実行文
    if area == "ic" or area == "工業都市":
        map = ic
        name = 'Industrial_City'
    elif area == "sh" or area == "瀬浜":
        map = sh
        name = 'Sehama'
    elif area == "cc" or area == "臨海都市":
        map = cc
        name = 'Coastal_City'
    elif area == "hm" or area == "浜口":
        map = hm
        name = 'Hamaguchi'
    elif area== "si" or area == "四央島":
        map = si
        name = 'Shiojima_Island'
    elif area == "ph" or area == "トウヒが丘":
        map = ph
        name = 'Pine_Hill'
    elif area == "sn" or area == "白根":
        map = sn
        name = 'Shirane'
    elif area == 'br' or area == "伯林":
        map = br
        name = "Berlin"
    elif area == 'a':
        map = all
        name = "Integrated"
    else:
        map = list(map(int, area.split()))
        name = "new"
    #integrate(mkimlist2d()).save('./new3.png')
    return integrate(mkimlist2d(*map)), name