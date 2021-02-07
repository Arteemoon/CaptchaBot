
import numpy as np
import cv2
from pathlib import Path
 

class Captcha:

    def __init__(self, filename, num):
        self.filename = filename
        self.num = num
        self._x = 100
        self._y = 150

    def create(self):
        """ create capture photo """
        img = np.zeros((256, 512, 3), np.uint8)
        img[:, :, :] = 255
        
        font = cv2.FONT_HERSHEY_COMPLEX
        cv2.putText(img, self.num, (self._x, self._y), font, 4, color=(0, 0, 255), thickness=2)
        cv2.imwrite(self.filename, img) 
        return self.filename
        # есть ограниченное кол-во вариантов выбора шрифта
        # FONT_HERSHEY_COMPLEX
        # FONT_HERSHEY_COMPLEX_SMALL
        # FONT_HERSHEY_DUPLEX
        # FONT_HERSHEY_PLAIN
        # FONT_HERSHEY_SCRIPT_COMPLEX
        # FONT_HERSHEY_SCRIPT_SIMPLEX
        # FONT_HERSHEY_SIMPLEX
        # FONT_HERSHEY_TRIPLEX
        # FONT_ITALIC