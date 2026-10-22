
import os
import csv
from datetime import datetime


def load_seen_codes(path):
    """读取 CSV 中历史记录过的条码。"""
    codes = set()

    if not os.path.exists(path):
        return codes

    try:
        with open(
            path, "r",
            newline="",
            encoding="utf-8-sig"
        ) as f:
            for row in csv.DictReader(f):
                code_type = (row.get("条码类型") or "").strip()
                data = (row.get("识别内容") or "").strip()

                if code_type and data:
                    codes.add((code_type, data))

    except (OSError, csv.Error) as e:
        print("读取历史记录失败：", e)

    return codes


def save_record(img, code_type, data, csv_path, image_dir):
    """保存识别图片并将识别结果写入 CSV。"""
    os.makedirs(image_dir, exist_ok=True)

    now = datetime.now()
    time_text = now.strftime("%Y-%m-%d %H:%M:%S")
    filename = now.strftime("%Y%m%d_%H%M%S_%f") + ".jpg"
    save_path = os.path.join(image_dir, filename)

    # 先保存图片
    image_saved = cv2_imwrite(img, save_path)

    if not image_saved:
        print("图片保存失败：", save_path)
        return False

    try:
        # 文件不存在或为空时，写入表头
        need_header = (
            not os.path.exists(csv_path)
            or os.path.getsize(csv_path) == 0
        )

        with open(
            csv_path, "a",
            newline="",
            encoding="utf-8-sig"
        ) as f:
            writer = csv.writer(f)

            if need_header:
                writer.writerow(["识别时间", "条码类型", "识别内容"])

            writer.writerow([time_text, code_type, data])

    except (OSError, csv.Error) as e:
        print("CSV 保存失败：", e)
        print("图片已保存，但记录可能未写入：", save_path)
        return False

    print("识别时间：", time_text)
    print("条码类型：", code_type)
    print("识别内容：", data)
    print("图片已保存：", save_path)
    print("识别记录已保存：", csv_path)

    return True


def cv2_imwrite(img, path):
    """单独封装图片保存，便于统一处理保存错误。"""
    try:
        import cv2
        return cv2.imwrite(path, img)
    except (OSError, cv2.error) as e:
        print("图片保存异常：", e)
        return False
