
import cv2
from pyzbar.pyzbar import decode
from datetime import datetime
from collections import deque
import os


# 打开电脑摄像头
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("没有检测到摄像头")
    exit()


# 用集合保存记录过的条码
seen_codes = set()

# 保存最近 5 帧中识别到的条码
recent_frames = deque(maxlen=5)

# 设置识别记录文件
record_file2 = "pyzbar_records.txt"
record_img2 = "pyzbar_images"

# 创建图片保存目录
os.makedirs(record_img2, exist_ok=True)


# EAN-13 条形码校验
def is_valid_ean13(code):
    if len(code) != 13 or not code.isdigit():
        return False

    digits = [int(c) for c in code]

    total = sum(digits[i] for i in range(12) if i % 2 == 0)
    total += 3 * sum(digits[i] for i in range(12) if i % 2 == 1)

    check_digit = (10 - total % 10) % 10

    return check_digit == digits[12]


try:
    while True:
        # 获取摄像头当前的一帧画面
        ret, img = cap.read()

        if not ret:
            print("无法获取摄像头画面")
            break

        # 检测并解码二维码、条形码
        results = decode(img)

        # 当前一帧识别到的有效条码
        frames_codes = set()

        for result in results:
            # 1. 获取识别内容
            data = result.data.decode("utf-8", errors="replace")

            # 2. 获取条码的类型
            code_type = result.type

            # 先校验 EAN-13
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
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                3
            )

            # 显示条码类型和内容
            label = f"{code_type}: {data}"

            cv2.putText(
                img,
                label[:50],
                (x, max(y - 10, 25)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
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

            # 写入日志
            with open(record_file2, "a", encoding="utf-8") as f:
                f.write(f"识别时间：{time_text}\n")
                f.write(f"条码类型：{code_type}\n")
                f.write(f"识别内容：{data}\n")
                f.write(f"图片路径：{save_path}\n")
                f.write("-" * 40 + "\n")

            # 图片和日志保存后，记录为已处理
            seen_codes.add(code)

            print("识别时间：", time_text)
            print("条码类型：", code_type)
            print("识别内容：", data)
            print("图片已保存：", save_path)
            print("识别记录已保存：", record_file2)

        # 显示实时画面
        cv2.imshow("条码识别", img)

        # 按 q 键退出——需要将鼠标焦点放在窗口上
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("程序已退出")
