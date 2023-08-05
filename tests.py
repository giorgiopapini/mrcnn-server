import requests
import numpy as np
import cv2


def get_mask():
    url = "http://127.0.0.1:8000/mrcnn/mask-image?api-key=000"
    files = {'file': open('000.png', 'rb')}
    res = requests.post(url, files=files)
    print(res.content)
    arr = np.frombuffer(res.content, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    cv2.imshow("img", img)
    cv2.waitKey(0)

get_mask()