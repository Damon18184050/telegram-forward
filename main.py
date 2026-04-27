import time
import requests

TOKEN = "8604959641:AAE-x8_OddNsZcv6Dumv251TLlcSyNomCJU"
SOURCE_CHAT_ID = -1003983646730
TARGET_CHAT_ID = -1001174798090

# 👇 追加内容
FOOTER = "\n\n下单飞机：@huangdaozhu（3分钟没回复弹语音或者打下面电话）\n性福热线：09516865555"

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
offset = None

media_groups = {}

print("机器人已启动，开始监听...")


def send_media_group(group_id):
    items = media_groups.pop(group_id, [])

    media = []
    for item in items:
        post = item["post"]

        if "photo" in post:
            file_id = post["photo"][-1]["file_id"]
            media_item = {
                "type": "photo",
                "media": file_id
            }
        elif "video" in post:
            file_id = post["video"]["file_id"]
            media_item = {
                "type": "video",
                "media": file_id
            }
        else:
            continue

        # 👉 只在第一条加文字（避免重复）
        if "caption" in post and len(media) == 0:
            media_item["caption"] = post["caption"] + FOOTER

        media.append(media_item)

    if media:
        res = requests.post(
            f"{BASE_URL}/sendMediaGroup",
            json={
                "chat_id": TARGET_CHAT_ID,
                "media": media
            },
            timeout=30
        )
        print("相册转发结果:", res.text)


while True:
    try:
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset

        r = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=40)
        data = r.json()

        now = time.time()

        for update in data.get("result", []):
            offset = update["update_id"] + 1

            post = update.get("channel_post")
            if not post:
                continue

            chat_id = post["chat"]["id"]
            message_id = post["message_id"]

            if chat_id != SOURCE_CHAT_ID:
                continue

            group_id = post.get("media_group_id")

            # =========================
            # 👉 相册处理
            # =========================
            if group_id:
                if group_id not in media_groups:
                    media_groups[group_id] = []

                media_groups[group_id].append({
                    "post": post,
                    "time": now
                })

                print("收到相册消息:", group_id, message_id)

            # =========================
            # 👉 单条消息处理
            # =========================
            else:
                text = None

                if "caption" in post:
                    text = post["caption"]
                elif "text" in post:
                    text = post["text"]

                # 👉 有文字 → 自己发送（加客服信息）
                if text:
                    text = text + FOOTER

                    res = requests.post(
                        f"{BASE_URL}/sendMessage",
                        json={
                            "chat_id": TARGET_CHAT_ID,
                            "text": text
                        },
                        timeout=20
                    )
                else:
                    # 👉 没文字 → 原样复制
                    res = requests.post(
                        f"{BASE_URL}/copyMessage",
                        json={
                            "chat_id": TARGET_CHAT_ID,
                            "from_chat_id": SOURCE_CHAT_ID,
                            "message_id": message_id
                        },
                        timeout=20
                    )

                print("单条转发结果:", res.text)

        # 👉 相册延迟发送（合并）
        for group_id in list(media_groups.keys()):
            first_time = media_groups[group_id][0]["time"]
            if now - first_time >= 2:
                send_media_group(group_id)

    except Exception as e:
        print("ERROR:", e)

    time.sleep(1)
