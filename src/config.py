"""项目配置。

普通用户只需要修改本文件，不必改动源码。
"""

from pathlib import Path

# 项目根目录（src 的上一级）。所有路径都基于这里，
# 因此在任意目录下启动程序，记录文件和截图目录位置都不会变。
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------
# 摄像头
# ---------------------------

# 默认摄像头编号，多摄像头设备可改为 1、2 等
CAMERA_INDEX = 0


# ---------------------------
# 识别与保存
# ---------------------------

# 记录文件与截图目录
RECORD_FILE = BASE_DIR / "pyzbar_records.csv"
IMAGE_DIR = BASE_DIR / "pyzbar_images"

# 多帧确认：最近 FRAME_WINDOW 帧中至少出现 MIN_CONFIRM_FRAMES 次
FRAME_WINDOW = 5
MIN_CONFIRM_FRAMES = 4

# 识别到有效网址二维码后，是否自动用默认浏览器打开
AUTO_OPEN_URL = True

# 成功记录时是否响铃提示
BEEP_ON_RECORD = False

# 识别窗口标题
WINDOW_NAME = "条码识别"


# ---------------------------
# MQTT（默认关闭）
# ---------------------------

# 只有需要把识别结果实时推送给其他系统时才开启。
# 开启后需要先在本机安装并启动 Mosquitto：
#     sudo apt install mosquitto
# 未启用或连接失败时，不影响识别、截图与 CSV 记录。
MQTT_ENABLED = False

MQTT_BROKER_HOST = "127.0.0.1"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "opencv/barcode/result"
MQTT_QOS = 1
MQTT_RETAIN = False
MQTT_KEEPALIVE = 60

# 客户端 ID 前缀，实际 ID 会自动附加随机后缀，避免多实例互相踢下线
MQTT_CLIENT_ID_PREFIX = "opencv_barcode_publisher"
