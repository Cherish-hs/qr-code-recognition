# scanner.py

import cv2
from pyzbar.pyzbar import decode
'''
    扫描二维码
'''

# CLAHE 对象可以跨帧复用，只创建一次，避免每帧重复分配
_CLAHE = cv2.createCLAHE(
    clipLimit=2.0,
    tileGridSize=(8, 8)
)


def scan_codes(img):
    gray = cv2.cvtColor(
        img, cv2.COLOR_BGR2GRAY
    )

    enhanced = _CLAHE.apply(gray)

    return decode(enhanced)