import cv2
import numpy as np
import glob
import io
from PIL import Image, ImageFilter

def cv2pil(image):
    ''' OpenCV型 -> PIL型 '''
    new_image = image.copy()
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
    new_image = Image.fromarray(new_image)
    return new_image

#fp:file object
def detect_map(fp):
    #ファイルオブジェクトからcv2に読み込み
    img_stream = io.BytesIO(fp.read())
    img = cv2.imdecode(np.frombuffer(img_stream.read(), np.uint8),1)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 地図枠の色範囲
    #（BGRで[148, 188,211]と[107, 133, 151]）
    # print(cv2.cvtColor(np.uint8([[[148, 188,211]]]), cv2.COLOR_BGR2HSV))
    lower = np.array([18,70,125])
    upper = np.array([19,85,220])

    # Threshold the HSV image to get only colors
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.bitwise_not(mask)

    #マスク画像から輪郭を探す
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    #地図枠の候補をリストアップ
    flame_can = []
    for i in range(0, len(contours)):
        if len(contours[i]) > 0:
            #remove small objects
            if cv2.contourArea(contours[i]) < 10000 or cv2.contourArea(contours[i]) > 1500000:
                continue

            rect = contours[i]
            flame_can.append(cv2.boundingRect(rect))

    w_can = [row[2] for row in flame_can]
    w=min(w_can)
    flame = flame_can[w_can.index(w)]
    x,y,w,h= flame
    l = min([w,h])

    pil_img = cv2pil(img)
    pil_img = pil_img.crop((x,y,x+l,y+l))
    pil_img = pil_img.resize((128,128), 0)
    return pil_img