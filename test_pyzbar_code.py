import cv2   # 调用OpenCV功能模块
from pyzbar.pyzbar import decode  # 调用pyzbar模块的decode函数，检测二维码和条形码
from datetime import datetime
from collections import deque   # 保存和管理最近几帧的识别结果 队列
import os  # 操作文件
import csv
import webbrowser      # 负责打开浏览器
from urllib.parse import urlparse  # 判断识别的内容是不是网址 

# 用集合保存记录过的条码
seen_codes = set()

# 保存最近 5 帧中识别到的条码
recent_frames = deque(maxlen=5)

# 设置识别记录文件
record_file2 = "pyzbar_records.csv"
record_img2 = "pyzbar_images"

# 创建图片保存目录   目录已经存在，不创建，不报错
os.makedirs(record_img2, exist_ok=True)


# ------EAN-13 条形码校验  返回校验结果  True/False
def is_valid_ean13(code):

    # 检查是否13位  且是否全为数字
    if len(code) != 13 or not code.isdigit():
        return False


    # 列表推导式，把每个数字字符串换成整数
    digits = [int(c) for c in code]

    total = sum(digits[i] for i in range(12) if i % 2 == 0)
    total += 3 * sum(digits[i] for i in range(12) if i % 2 == 1)

    check_digit = (10 - total % 10) % 10

    return check_digit == digits[12]


# ---------增加判断网址的函数
def get_valid_url(data):
    """只接受 http 或 https 网址。"""
    try:
        parsed = urlparse(data.strip())
        if(
            parsed.scheme in ("http", "https")
            and parsed.hostname
            and not any(c.isspace() for c in data)
        ):
            return data.strip()
    except ValueError:
        pass
    return None

# -----打开电脑摄像头
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("没有检测到摄像头")
    exit()

pending_url = None

try:
    while True:
        # 获取摄像头当前的一帧画面
        # ret  是读取结果 true 成功 false 失败
        # img  读的图片数据
        ret, img = cap.read()

        if not ret:
            print("无法获取摄像头画面")
            break

        # 检测并解码二维码、条形码
        results = decode(img)

        # 当前一帧识别到的有效条码集合
        frames_codes = set()

       

        for result in results:
            # 1. 获取识别的原始内容并将字节数据转换成python字符串
            data = result.data.decode("utf-8", errors="replace")

            # 2. 获取条码的类型
            code_type = result.type

            # 如果是二维码，判断是否是有效网址
            # 如果是有效网址，保存到peding_url
            # 否则，忽略该条码
            if code_type == "QRCODE":
                url = get_valid_url(data)
                if url:
                    pending_url = url

         

            # 如果是条形码，并且校验结果不符合，忽略该条码
            # 否则，保存当前帧识别到的条码类型和内容
            if code_type == "EAN13" and not is_valid_ean13(data):
                print("条码校验失败，忽略", data)
                continue

            # 保存当前帧识别到的条码类型和内容
            frames_codes.add((code_type, data))

            # 3. 获取识别框的位置和尺寸 
            x, y, w, h = result.rect

            # 4. 绘制矩形框
            cv2.rectangle(
                img,
                (x, y),  # 识别框的左上角坐标
                (x + w, y + h),  # 识别框的右下角坐标
                (0, 255, 0),
                3
            )

            # 显示条码类型和内容
            label = f"{code_type}: {data}"

            # 将文字绘制到图像上
            cv2.putText(
                img,
                label[:50],
                (x, max(y - 10, 25)),
                cv2.FONT_HERSHEY_SIMPLEX,  # 字体类型
                0.6,  # 字体大小    
                (0, 255, 0),  # 文字颜色
                2,  # 文字粗细
            )

        # 每一帧都加入统计，即使当前帧没有识别到条码
        recent_frames.append(frames_codes)

        # 统计最近 5 帧中，每个条码出现了多少帧
        code_counts = {}

        for frame in recent_frames:
            for code in frame:
                code_counts[code] = code_counts.get(code, 0) + 1

        # 最近 5 帧中至少 4 帧识别到同一个码，才允许保存
        for code, count in code_counts.items():
            code_type, data = code

            if count < 4:
                continue

            # 同一种类型、同样的内容，只保存一次
            if code in seen_codes:
                continue

            now = datetime.now()
            time_text = now.strftime("%Y-%m-%d %H:%M:%S")
            filename = now.strftime("%Y%m%d_%H%M%S_%f") + ".jpg"
            save_path = os.path.join(record_img2, filename)

            # 保存图片
            image_saved = cv2.imwrite(save_path, img)

            if not image_saved:
                print("图片保存失败：", save_path)
                continue

            # 写表头
            if not os.path.exists(record_file2) or os.path.getsize(record_file2) == 0:
                with open(record_file2, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(["识别时间", "条码类型", "识别内容"])

            # 写入日志    修改 ---将数据保存到csv中
            with open(record_file2, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f) 
                writer.writerow([
                    time_text,
                    code_type,
                    data,
                  
                ])
                
            # 图片和日志保存后，记录为已处理
            seen_codes.add(code)

            print("识别时间：", time_text)
            print("条码类型：", code_type)
            print("识别内容：", data)
            print("图片已保存：", save_path)
            print("识别记录已保存：", record_file2)
            print("按o打开网址，按q退出程序")

        # 显示实时画面
        cv2.imshow("条码识别", img)


        key = cv2.waitKey(1) & 0xFF
        if key == ord("o"):
            if pending_url:
                webbrowser.open(pending_url)
                print("已打开网址：", pending_url)      
            else:
                print("当前帧没有识别到有效网址")
        elif key == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("程序已退出")
