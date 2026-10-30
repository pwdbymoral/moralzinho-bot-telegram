import json
import os
import re
import secrets
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DICE_EXPRESSION = re.compile(
    r"(?P<count>\d{0,3})d(?P<sides>\d{1,5})(?:\s*(?P<sign>[+-])\s*(?P<modifier>\d{1,5}))?",
    re.IGNORECASE,
)
COMMAND = re.compile(r"^/([a-z0-9_]+)(?:@[a-z0-9_]+)?(?:\s+(.*))?$", re.IGNORECASE | re.DOTALL)
DEFAULT_REPLIES = {"corno": "corno eh tu"}
BALL_ANSWERS = (
    "Com certeza.",
    "É provável.",
    "As chances são boas.",
    "Sem dúvida.",
    "Não conte com isso.",
    "Minha resposta é não.",
    "Melhor perguntar de novo.",
    "Não consigo prever agora.",
)
BOT_COMMANDS = [
    {"command": "start", "description": "Começar a usar o bot"},
    {"command": "ajuda", "description": "Ver os comandos disponíveis"},
    {"command": "d20", "description": "Rolar um dado de 20 lados"},
    {"command": "rolar", "description": "Rolar dados de RPG"},
    {"command": "moeda", "description": "Lançar uma moeda"},
    {"command": "8ball", "description": "Perguntar à bola 8"},
    {"command": "escolher", "description": "Escolher entre opções"},
]
HELP_TEXT = (
    "Fala pai! Eu faço umas rolagens e respondo umas coisas:\n\n"
    "/d20 — rola um d20\n"
    "/d20 vantagem ou /d20 desvantagem — rola com vantagem/desvantagem\n"
    "/rolar 2d6+3 — rola dados de RPG (até 20 dados)\n"
    "/moeda — cara ou coroa\n"
    "/8ball pergunta — resposta da bola 8\n"
    "/escolher pizza | hambúrguer — escolhe uma opção\n\n"
    "E se alguém falar corno, eu respondo."
)


def is_healthy():
    try:
        with open("/proc/1/cmdline", "rb") as command_line:
            return b"bot.py" in command_line.read().split(b"\0")
    except OSError:
        return False


def load_custom_replies():
    replies = DEFAULT_REPLIES.copy()
    configured = os.getenv("CUSTOM_REPLIES_JSON", "{}").strip()
    try:
        custom = json.loads(configured or "{}")
        if not isinstance(custom, dict):
            raise ValueError("esperado um objeto JSON")
    except (json.JSONDecodeError, ValueError):
        print("CUSTOM_REPLIES_JSON inválido; usando apenas a resposta padrão.", file=sys.stderr)
        custom = {}

    for trigger, response in custom.items():
        if isinstance(trigger, str) and trigger.strip() and isinstance(response, str) and response.strip():
            replies[trigger.strip()] = response.strip()

    return sorted(
        (
            (re.compile(rf"(?<!\w){re.escape(trigger)}(?!\w)", re.IGNORECASE), response)
            for trigger, response in replies.items()
        ),
        key=lambda item: len(item[0].pattern),
        reverse=True,
    )


def roll_d20(mode=""):
    mode = mode.casefold().strip()
    if mode in {"", "normal"}:
        result = secrets.randbelow(20) + 1
        note = " (20 natural!)" if result == 20 else " (1 natural!)" if result == 1 else ""
        return f"🎲 d20: {result}{note}"

    if mode in {"vantagem", "adv", "vantage"}:
        values = [secrets.randbelow(20) + 1 for _ in range(2)]
        return f"🎲 d20 com vantagem: [{values[0]}, {values[1]}] → {max(values)}"

    if mode in {"desvantagem", "dis", "disadvantage"}:
        values = [secrets.randbelow(20) + 1 for _ in range(2)]
        return f"🎲 d20 com desvantagem: [{values[0]}, {values[1]}] → {min(values)}"

    return "Uso: /d20, /d20 vantagem ou /d20 desvantagem."


def roll_dice(expression):
    match = DICE_EXPRESSION.fullmatch(expression.strip())
    if not match:
        return "Formato: /rolar 2d6+3 (ou /rolar d20)."

    count = int(match.group("count") or "1")
    sides = int(match.group("sides"))
    modifier_text = match.group("modifier")
    modifier = int(modifier_text or "0")
    if match.group("sign") == "-":
        modifier = -modifier

    if not 1 <= count <= 20 or not 2 <= sides <= 1000 or abs(modifier) > 10000:
        return "Limites: 1–20 dados, 2–1000 lados e modificador até 10000."

    values = [secrets.randbelow(sides) + 1 for _ in range(count)]
    total = sum(values) + modifier
    notation = f"{count}d{sides}"
    detail = ", ".join(str(value) for value in values)
    if modifier_text is not None:
        sign = "+" if modifier >= 0 else "−"
        notation += f"{sign}{abs(modifier)}"
        return f"🎲 {notation}: [{detail}] {sign} {abs(modifier)} = {total}"
    return f"🎲 {notation}: [{detail}] = {total}"


def reply_to(text, custom_replies):
    command_match = COMMAND.match(text.strip())
    if command_match:
        command, arguments = command_match.groups()
        command = command.casefold()
        arguments = (arguments or "").strip()

        if command in {"start", "help", "ajuda"}:
            return HELP_TEXT
        if command == "d20":
            return roll_d20(arguments)
        if command == "rolar":
            return roll_dice(arguments)
        if command == "moeda":
            return f"🪙 {secrets.choice(('Cara', 'Coroa'))}!"
        if command == "8ball":
            return f"🎱 {secrets.choice(BALL_ANSWERS)}"
        if command == "escolher":
            options = [option.strip() for option in arguments.split("|") if option.strip()]
            if len(options) < 2:
                return "Uso: /escolher opção 1 | opção 2 (ou mais opções)."
            return f"🎯 Escolhi: {secrets.choice(options)}"
        return None

    for pattern, response in custom_replies:
        if pattern.search(text):
            return response
    return None


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
    custom_replies = load_custom_replies()
    print("Bot iniciado. Aguardando mensagens...")

    try:
        telegram(token, "setMyCommands", commands=json.dumps(BOT_COMMANDS, ensure_ascii=False))
    except (HTTPError, URLError, TimeoutError, RuntimeError) as error:
        print(str(error).replace(token, "[token oculto]"), file=sys.stderr)

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

            if (message.get("from") or {}).get("is_bot"):
                continue

            reply = reply_to(text, custom_replies)
            if reply is None:
                continue

            try:
                telegram(
                    token,
                    "sendMessage",
                    chat_id=message["chat"]["id"],
                    text=reply,
                    reply_parameters=json.dumps({"message_id": message["message_id"]}),
                )
            except (HTTPError, URLError, TimeoutError, RuntimeError) as error:
                print(str(error).replace(token, "[token oculto]"), file=sys.stderr)


if __name__ == "__main__":
    if sys.argv[1:] == ["--healthcheck"]:
        sys.exit(0 if is_healthy() else 1)
    main()
