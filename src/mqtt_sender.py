"""MQTT 结果发送器（可选功能）。

MQTT 默认关闭，通过 config.MQTT_ENABLED 开启。
任何连接或发布失败都只打印提示，不会中断主程序的识别与保存流程。
"""

import json
import uuid
from datetime import datetime

import config

# 未安装 paho-mqtt 时也不影响主程序运行
try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


class MQTTSender:

    def __init__(self):

        self.client = None
        self.available = False

        if not config.MQTT_ENABLED:
            print("【MQTT】未启用（config.MQTT_ENABLED = False）")
            return

        if mqtt is None:
            print("【MQTT】未安装 paho-mqtt，已跳过 MQTT 功能")
            return

        client_id = (
            f"{config.MQTT_CLIENT_ID_PREFIX}-{uuid.uuid4().hex[:6]}"
        )

        try:
            self.client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=client_id
            )

            self.client.connect(
                config.MQTT_BROKER_HOST,
                config.MQTT_BROKER_PORT,
                keepalive=config.MQTT_KEEPALIVE
            )

            # 启动后台网络循环，处理消息通信
            self.client.loop_start()

            self.available = True

            print(
                f"【MQTT】已连接 {config.MQTT_BROKER_HOST}"
                f":{config.MQTT_BROKER_PORT}"
                f"，client_id={client_id}"
            )

        except Exception as e:
            self.client = None
            self.available = False
            print(f"【MQTT】连接失败，已跳过 MQTT 功能：{e}")

    def publish_result(self, code_type, content):
        """发布一条识别结果，成功提交返回 True。"""

        if not self.available:
            return False

        # 将识别结果组织成 JSON 数据
        data = {
            "barcode_type": code_type,
            "content": content,
            "timestamp": datetime.now().astimezone().isoformat(
                timespec="seconds"
            )
        }

        payload = json.dumps(
            data,
            ensure_ascii=False
        )

        result = self.client.publish(
            config.MQTT_TOPIC,
            payload=payload,
            qos=config.MQTT_QOS,
            retain=config.MQTT_RETAIN
        )

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"【MQTT】消息已提交：{payload}")
            return True

        print(f"【MQTT】发布失败，错误码：{result.rc}")
        return False

    def close(self):
        """断开连接，可重复调用。"""

        if self.client is None:
            return

        try:
            # 先发送断开报文，再停止后台网络线程
            self.client.disconnect()
            self.client.loop_stop()

        except Exception as e:
            print(f"【MQTT】关闭连接时出错：{e}")

        finally:
            self.client = None
            self.available = False
