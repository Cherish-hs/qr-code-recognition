import cv2
from datetime import datetime
img = cv2.imread("images/qr.jpg")   # 读取图片

# 1.检查图片是否读取成功
if img is None:
    print("图片读取失败")
    exit()

detector = cv2.QRCodeDetector()   # 二维码识别器
data, points, _ = detector.detectAndDecode(img)    # 检测并且解码  内容 位置 其他

print("二维码内容：", data)
print("二维码位置：", points)

# 2. 把识别记录保存到本地
with open('qr_records.txt',"a",encoding="utf-8") as f:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if data:
        f.write(f"识别时间：{now}\n")
        f.write(f"识别内容：{data}\n")
        f.write(f"图片路径：images/qr.jpg\n")
        f.write("识别状态：成功\n")
    else:
        f.write(f"识别时间：{now}\n")
        f.write(f"识别内容：无\n")
        f.write(f"图片路径：images/qr.jpg\n")
        f.write("识别状态：失败\n")
    f.write("-" * 30 + "\n")


# 3. 绘制二维码边框
if points is not None:
    points = points.astype(int).reshape(-1, 2)

    # 用绿色线条连接二维码的四个角
    cv2.polylines(
        img,     
        [points],   # 要连接的角点集合
        True,   # 闭合
        (0, 255, 0),  # 颜色
        3   # 线条宽度，像素
    )

    # 4. 将框好的图片保存   # ---- 不会自动创建该文件夹，需要手动创建
    cv2.imwrite("processed_images/qr.jpg", img)
    # 创建窗口，显示框好的图片
    cv2.imshow("QR Code Detection", img)   
    # 等待键盘输入
    cv2.waitKey(0)
    cv2.destroyAllWindows()