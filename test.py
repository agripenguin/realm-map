import io
import cv2
import numpy as np

img_stream = io.BytesIO(open("2020-09-13.png", 'rb').read())
img = cv2.imdecode(np.frombuffer(img_stream.read(), np.uint8),1)

cv2.imshow('img', img)
cv2.waitKey(0)