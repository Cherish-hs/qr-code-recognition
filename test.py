import cv2
from datetime import datetime
# 1. 打开电脑默认摄像头
cap = cv2.VideoCapture(0)

# 检查摄像头是否打开成功
if not cap.isOpened():
    print("摄行头打开失败,请检查摄行头是否可用")
    exit()

# 2. 创建二维码识别器
detector = cv2.QRCodeDetector()

# 记录上一次识别到的内容，避免每次识别都打印
last_data = ""


# 设置识别记录文件
record_file = "qr_records.txt"
record_img = "processed_images"
try:
    while True:
        # 3. 获取摄像头当前的一帧画面
        ret, img = cap.read()
        if not ret:
            print("无法获取摄像头画面")
            break

        # 4.检测并解码
        data, points, _ = detector.detectAndDecode(img)

        # 5. 如果检测到画框
        if points is not None:
            points = points.astype(int).reshape(-1,2)
            cv2.polylines(
                img,
                [points],
                True,
                (0, 255, 0),
                3
            )
        # 6. 识别到新的二维码内容时，保存记录输出到终端
        if data and data != last_data:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print("识别时间：", now)
            print("识别内容：", data)


            # 将识别并框住的图片保存
            filename = now + ".jpg"
            cv2.imwrite(record_img + "/" + filename, img)
            print("识别并框住的图片已保存到：",record_img + "/" + filename)

            # 以追加模式打开文本内容
            with open(record_file, "a",encoding="utf-8") as f:
                f.write(f"识别时间：{now}\n")
                f.write(f"识别内容：{data}\n")
                f.write("-" * 40 + "\n")
            print("识别记录已保存到：",record_file)
            last_data = data
        
        # 7.显示实时画面
        cv2.imshow("二维码识别", img)

        # 按 q 键退出  -----这个按 q 需要将鼠标聚焦在窗口上
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    # 8. 释放摄像头和关闭窗口
    cap.release()
    cv2.destroyAllWindows()
    print("程序已退出")