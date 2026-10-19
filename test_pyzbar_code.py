import cv2
from pyzbar.pyzbar import decode
from datetime import datetime
# 打开电脑摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("某有瞅到")
    exit()

# 不用像qr那样创建识别器，直接用decode函数
last_data = ""


# 设置识别记录文件
record_file2 = "pyzbar_records.txt"
record_img2 = "pyzbar_images"

try:
    while True:
        # 获取摄像头当前的一帧画面
        ret, img = cap.read()
        if not ret:
            print("无法获取摄像头画面")
            break
        # 检测并解码二维码，条形码
        results = decode(img)
        for result in results:
            # 1. 获取识别内容
            data = result.data.decode("utf-8", errors="replace")

            # 2.获取条形码的类型
            code_type = result.type
            # 3.获取识别狂的位置和尺寸
            x,y,w,h = result.rect
            # 4. 绘制矩形框
            cv2.rectangle(
                img,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                3
            )
            if data and data != last_data:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("识别时间：", now)
                print("条码类型：", code_type)
                print("识别内容：", data)

                filename = now + ".jpg"
                cv2.imwrite(record_img2 + "/" + filename, img)
                print("识别并框住的图片已保存到：",record_img2 + "/" + filename)

                  # 以追加模式打开文本内容
                with open(record_file2, "a",encoding="utf-8") as f:
                    f.write(f"识别时间：{now}\n")
                    f.write(f"条码类型：{code_type}\n")
                    f.write(f"识别内容：{data}\n")
                    f.write("-" * 40 + "\n")
                print("识别记录已保存到：",record_file2)
                last_data = data
        
        # 显示实时画面
        cv2.imshow("条码识别", img)

        # 按 q 键退出  -----这个按 q 需要将鼠标聚焦在窗口上
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("程序已退出")



