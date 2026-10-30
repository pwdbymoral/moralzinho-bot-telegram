import json
import os
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


CORNO = re.compile(r"\bcorno\b", re.IGNORECASE)


def telegram(token, method, **params):
    url = f"https://api.telegram.org/bot{token}/{method}"
    request = Request(url, data=urlencode(params).encode())

    with urlopen(request, timeout=40) as response:
        result = json.load(response)

    if not result.get("ok"):
        raise RuntimeError(result.get("description", "Erro na API do Telegram"))

    return result["result"]


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        sys.exit("Defina a variável TELEGRAM_BOT_TOKEN antes de iniciar o bot.")

    offset = None
    print("Bot iniciado. Aguardando mensagens...")

    while True:
        try:
            params = {"timeout": 30, "allowed_updates": json.dumps(["message"])}
            if offset is not None:
                params["offset"] = offset
            updates = telegram(token, "getUpdates", **params)
        except (HTTPError, URLError, TimeoutError, RuntimeError) as error:
            print(str(error).replace(token, "[token oculto]"), file=sys.stderr)
            time.sleep(3)
            continue

        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message", {})
            text = message.get("text") or message.get("caption", "")

            if (message.get("from") or {}).get("is_bot") or not CORNO.search(text):
                continue

            try:
                telegram(
                    token,
                    "sendMessage",
                    chat_id=message["chat"]["id"],
                    text="corno eh tu",
                    reply_parameters=json.dumps({"message_id": message["message_id"]}),
                )
            except (HTTPError, URLError, TimeoutError, RuntimeError) as error:
                print(str(error).replace(token, "[token oculto]"), file=sys.stderr)


if __name__ == "__main__":
    main()
