
import time
from collections import deque

import cv2

import config
from scanner import scan_codes
from validators import is_valid_ean13, get_valid_url
from storage import load_seen_codes, save_record
from url_handler import open_url
from mqtt_sender import MQTTSender


# ---------------------------
# 1. 加载历史记录
# ---------------------------

seen_codes = load_seen_codes(config.RECORD_FILE)

print(f"已加载 {len(seen_codes)} 条历史条码记录")


# ---------------------------
# 2. 初始化多帧统计
# ---------------------------

recent_frames = deque(maxlen=config.FRAME_WINDOW)

# 当前程序运行期间，已经打开过的网址
opened_urls = set()

# 刚刚保存成功的条码，在此时间点之前继续显示 RECORDED 提示
just_recorded = {}


def main():

    # MQTT 为可选功能：未启用或连接失败时，不影响识别与保存
    mqtt_sender = MQTTSender()

    # ---------------------------
    # 4. 打开摄像头
    # ---------------------------

    cap = cv2.VideoCapture(config.CAMERA_INDEX)

    if not cap.isOpened():
        print("没有检测到摄像头")

        # 摄像头打开失败时，也关闭 MQTT 连接
        mqtt_sender.close()
        return

    print("摄像头已打开，按 q 退出程序")

    # 窗口内的状态提示，用于解释"为什么这次没有新增记录"
    status_text = ""
    status_color = (0, 255, 0)
    status_until = 0.0

    try:
        while True:

            # ---------------------------
            # 5. 读取一帧画面
            # ---------------------------

            ret, img = cap.read()

            if not ret:
                print("无法获取摄像头画面")
                break

            # ---------------------------
            # 6. 调用识别模块
            # ---------------------------

            results = scan_codes(img)

            # 当前帧通过基本验证的条码集合
            frames_codes = set()

            # 当前帧识别到的有效网址
            frame_urls = set()

            for result in results:

                data = result.data.decode(
                    "utf-8",
                    errors="replace"
                )

                code_type = result.type

                # ---------------------------
                # 7. 验证识别结果
                # ---------------------------

                if code_type == "EAN13":

                    if not is_valid_ean13(data):
                        print("条码校验失败，忽略：", data)
                        status_text = "INVALID EAN13"
                        status_color = (0, 0, 255)
                        status_until = time.time() + 1.5
                        continue

                elif code_type == "QRCODE":

                    url = get_valid_url(data)

                    # 本项目只接受包含有效网址的二维码
                    if url is None:
                        status_text = "URL QR ONLY"
                        status_color = (0, 0, 255)
                        status_until = time.time() + 1.5
                        continue

                    frame_urls.add(url)

                # 其他条码类型暂时保留原有行为

                frames_codes.add((code_type, data))

                # ---------------------------
                # 8. 绘制识别框和文字
                # ---------------------------

                x, y, w, h = result.rect

                cv2.rectangle(
                    img,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    3
                )

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

            # ---------------------------
            # 9. 记录当前帧并统计最近 5 帧
            # ---------------------------

            # 即使当前帧没有识别到条码，也加入空集合
            recent_frames.append(frames_codes)

            code_counts = {}

            for frame in recent_frames:
                for code in frame:
                    code_counts[code] = (
                        code_counts.get(code, 0) + 1
                    )

            # ---------------------------
            # 10. 多帧确认、打开网址、保存记录
            # ---------------------------

            for code, count in code_counts.items():

                # 最近若干帧中，至少命中 MIN_CONFIRM_FRAMES 次
                if count < config.MIN_CONFIRM_FRAMES:
                    continue

                code_type, data = code

                # 有效二维码达到多帧确认后，打开网址
                if code_type == "QRCODE":

                    url = get_valid_url(data)

                    if (
                        config.AUTO_OPEN_URL
                        and url
                        and url not in opened_urls
                    ):
                        opened_urls.add(url)
                        open_url(url)

                # 历史记录中存在，就不重复保存，也不重复发送 MQTT
                if code in seen_codes:

                    # 刚保存成功的那几秒，不要把绿色 RECORDED 覆盖成黄色
                    if just_recorded.get(code, 0.0) > time.time():
                        continue

                    status_text = "ALREADY RECORDED"
                    status_color = (0, 215, 255)
                    status_until = time.time() + 1.5
                    continue

                # 保存图片和 CSV
                saved = save_record(
                    img,
                    code_type,
                    data,
                    config.RECORD_FILE,
                    config.IMAGE_DIR
                )

                # 只有完整保存成功，才标记为已处理
                if saved:

                    seen_codes.add(code)
                    just_recorded[code] = time.time() + 2.0

                    status_text = "RECORDED"
                    status_color = (0, 255, 0)
                    status_until = time.time() + 2.0

                    if config.BEEP_ON_RECORD:
                        print("\a", end="", flush=True)

                    # 是否真的提交成功，由 publish_result 自己打印
                    mqtt_sender.publish_result(
                        code_type=code_type,
                        content=data
                    )

            # ---------------------------
            # 11. 显示画面并检查退出按键
            # ---------------------------

            if status_text and time.time() < status_until:
                cv2.putText(
                    img,
                    status_text,
                    (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    status_color,
                    2
                )

            cv2.imshow(config.WINDOW_NAME, img)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    finally:

        # ---------------------------
        # 12. 释放资源
        # ---------------------------

        cap.release()
        cv2.destroyAllWindows()

        # 【新增 MQTT】停止后台网络循环并断开连接
        mqtt_sender.close()

        print("程序已退出")


if __name__ == "__main__":
    main()
