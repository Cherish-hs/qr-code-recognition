import cv2

img = cv2.imread("images/qr.jpg")

detector = cv2.QRCodeDetector()
data, points, _ = detector.detectAndDecode(img)

print("二维码内容：", data)
print("二维码位置：", points)

if points is not None:
    points = points.astype(int).reshape(-1, 2)

    # 用绿色线条连接二维码的四个角
    cv2.polylines(
        img,
        [points],
        True,
        (0, 255, 0),
        3
    )

    cv2.imshow("QR Code Detection", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()