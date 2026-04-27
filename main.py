import time
import requests

TOKEN = "8604959641:AAFLVWtV9BdB4Qhreu5pqEOMgaWvyV41T2E"
SOURCE_CHAT_ID = -1003983646730
TARGET_CHAT_ID = -1001174798090

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
offset = None

print("机器人已启动，开始监听...")

while True:
    try:
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset

        r = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=40)
        data = r.json()

        for update in data.get("result", []):
            offset = update["update_id"] + 1

            post = update.get("channel_post")
            if not post:
                continue

            chat_id = post["chat"]["id"]
            message_id = post["message_id"]

            print("收到频道:", chat_id, "消息ID:", message_id)

            if chat_id == SOURCE_CHAT_ID:
                res = requests.post(
                    f"{BASE_URL}/copyMessage",
                    json={
                        "chat_id": TARGET_CHAT_ID,
                        "from_chat_id": SOURCE_CHAT_ID,
                        "message_id": message_id
                    },
                    timeout=20
                )
                print("转发结果:", res.text)

    except Exception as e:
        print("ERROR:", e)

    time.sleep(1)
