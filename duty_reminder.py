import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import datetime
import os

WEBHOOK = os.environ["WEBHOOK"]
SECRET = os.environ["SECRET"]

DUTY_TABLE = {
    "2026-01-26": {
        "night": [("赵帆", "18109210416")],
    },
    "2026-01-27": {
        "night": [("张志红", "15109299446")],
    },
    "2026-01-28": {
        "night": [("田明鑫", "15309463583")],
    },
    "2026-01-29": {
        "night": [("杜江炜", "18109299758")],
    },
    "2026-01-30": {
        "night": [("安瑞青", "18691488324")],
    },
    "2026-01-31": {
        "night": [("李忠峰", "18871905020")],
        "day":   [("刘佳宁", "18691315893")],
    },
    "2026-02-01": {
        "night": [("赵帆", "18109210416")],
        "day":   [("刘陇梅", "17802901101")],
    },
    "2026-02-02": {
        "night": [("杜江炜", "18109299758")],
    },
    "2026-02-03": {
        "night": [("田明鑫", "15309463583")],
    },
    "2026-02-04": {
        "night": [("李忠峰", "18871905020")],
    },
    "2026-02-05": {
        "night": [("安瑞青", "18691488324")],
    },
    "2026-02-06": {
        "night": [("张志红", "15109299446")],
    },
    "2026-02-07": {
        "day": [("胡占换", "18606509041")],
    },
}


def sign_url():
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{SECRET}"
    sign = base64.b64encode(
        hmac.new(
            SECRET.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
    )
    return f"{WEBHOOK}&timestamp={timestamp}&sign={urllib.parse.quote_plus(sign)}"


def send_msg(date_str, night=None, day=None):
    url = sign_url()

    content = f"【值班提醒】\n日期：{date_str}\n"
    mobiles = []

    if night:
        names = "、".join([n for n, _ in night])
        content += f"夜班值班人：{names}\n"
        mobiles += [m for _, m in night]

    if day:
        names = "、".join([n for n, _ in day])
        content += f"白班值班人：{names}\n"
        mobiles += [m for _, m in day]

    content += "请安排好相关工作。"

    data = {
        "msgtype": "text",
        "text": {"content": content},
        "at": {
            "atMobiles": mobiles,
            "isAtAll": False
        }
    }

    resp = requests.post(url, json=data)
    print("发送状态:", resp.status_code, resp.text)


def main():
    today = datetime.date.today().strftime("%Y-%m-%d")
    duty = DUTY_TABLE.get(today)

    if not duty:
        print(f"{today} 没有排班，不发送")
        return

    # 防重复发送：创建当天标记文件
    sent_file = f".sent_{today}.txt"
    if os.path.exists(sent_file):
        print(f"{today} 今日已发送提醒，退出")
        return
    # 创建标记文件
    with open(sent_file, "w") as f:
        f.write("sent")

    # 发送提醒
    send_msg(
        today,
        night=duty.get("night"),
        day=duty.get("day")
    )
    print(f"{today} 提醒已发送")


if __name__ == "__main__":
    main()
