import numpy as np
import cv2
from mss import mss
import time


with mss() as sct:
    bbox = (0, 0, 1600, 900)
    while True:
        start = time.time()
        img = sct.grab(bbox)
        img_np = np.array(img)
        frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        # cv2.imshow("frame", img_np)
        end = time.time()
        print(f'fps: {1 / (end - start)}')
        if cv2.waitKey(1) & 0Xff == ord('q'):
            break
        
cv2.destroyAllWindows()

