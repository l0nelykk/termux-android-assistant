import requests
import json
import os
import subprocess
import re
import urllib.parse
from datetime import datetime

MODEL = "qwen2.5:1.5b"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

# Константы с package names
PACKAGES = {
    "ютуб": "com.google.android.youtube",
    "хром": "com.android.chrome",
    "браузер": "com.android.chrome",
    "калькулятор": "com.google.android.calculator",
    "настройки": "com.android.settings",
    "звонки": "com.android.dialer",
    "телефон": "com.android.dialer",
    "галерея": "com.android.gallery3d",
    "камера": "com.android.camera",
    "спотифай": "com.spotify.music",
    "музыка": "com.spotify.music",
    "термукс": "com.termux",
}

URL_SCHEMES = {
    "com.google.android.youtube": "vnd.youtube://",
    "com.android.chrome": "https://google.com",
    "com.google.android.calculator": "calculator://",
    "com.android.settings": "settings://",
    "com.android.dialer": "tel://",
    "com.android.camera": "camera://",
    "com.spotify.music": "spotify://",
    "com.termux": "termux://",
    "com.yandex.music": "yandexmusic://",
}

SYSTEM_PROMPT = """Ты — Джарвис, AI-ассистент с доступом к Android.
Ты можешь выполнять команды на телефоне. На любую просьбу ты ОБЯЗАН вернуть ТОЛЬКО JSON, ничего больше.

Доступные команды (action):
- open_app: открыть приложение. params: {"package": "com.google.android.youtube"}
- play_music: включить музыку. params: {"artist": "deftones"}
- set_volume: громкость. params: {"level": 7} (число от 1 до 15)
- clipboard: скопировать текст. params: {"text": "строка"}
- notification: показать уведомление. params: {"title": "Заголовок", "message": "Текст"}
- flashlight_on: включить фонарик. params: {}
- flashlight_off: выключить фонарик. params: {}
- system_info: информация о системе (батарея, память). params: {}
- say_time: сказать текущее время. params: {}
- search_web: поиск в интернете. params: {"query": "запрос"}
- lock_screen: заблокировать экран. params: {}
- screenshot: сделать скриншот. params: {}

Формат ответа строго:
{"action": "команда", "params": {"ключ": "значение"}, "reply": "что сказать пользователю"}

ВАЖНО:
- Любую просьбу выключить фонарик понимаешь как flashlight_off
- Любую просьбу включить фонарик понимаешь как flashlight_on
- Для открытия приложений используй ТОЧНЫЕ package names из списка выше

Примеры:
"открой ютуб" → {"action": "open_app", "params": {"package": "com.google.android.youtube"}, "reply": "YouTube открыт, сэр."}
"выруби фонарик" → {"action": "flashlight_off", "params": {}, "reply": "Фонарик выключен, сэр."}
"сделай скриншот" → {"action": "screenshot", "params": {}, "reply": "Скриншот сохранён, сэр."}
"заблокируй экран" → {"action": "lock_screen", "params": {}, "reply": "Экран заблокирован, сэр."}
"""

def ask_jarvis(user_input):
    """Отправляет запрос модели, получает JSON"""
    prompt = f"{SYSTEM_PROMPT}\n\nПользователь: {user_input}\nДжарвис:"
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}  # Очень низкая температура для точных JSON
    }
    
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if resp.status_code == 200:
            response_text = resp.json()["response"].strip()
            return response_text
    except Exception as e:
        print(f"Ошибка подключения к Ollama: {e}")
    return None

def validate_action(data):
    """Проверяет, что JSON соответствует схеме"""
    required = ["action", "reply"]
    if not all(k in data for k in required):
        return False, "Отсутствуют обязательные поля"
    
    valid_actions = ["open_app", "play_music", "set_volume", "clipboard", 
                     "notification", "flashlight_on", "flashlight_off", 
                     "system_info", "say_time", "search_web", "lock_screen", "screenshot"]
    
    if data["action"] not in valid_actions:
        return False, f"Неизвестное действие: {data['action']}"
    
    return True, "OK"

def is_app_installed(package_name):
    """Проверяет, установлено ли приложение"""
    try:
        result = subprocess.run(["pm", "list", "packages", package_name], 
                              capture_output=True, text=True, timeout=5)
        return package_name in result.stdout
    except:
        return False

def execute_action(action_json):
    try:
        data = json.loads(action_json)
        
        # Валидация JSON
        is_valid, error_msg = validate_action(data)
        if not is_valid:
            return f"Ошибка валидации: {error_msg}"
        
        action = data.get("action")
        params = data.get("params", {})
        reply = data.get("reply", "Сделано, сэр.")
        
        print(f"⚡ Выполняю: {action}")
        
        # ─── ФОНАРИК ───
        if action == "flashlight_on":
            subprocess.run(["termux-torch", "on"], timeout=5)
        
        elif action == "flashlight_off":
            subprocess.run(["termux-torch", "off"], timeout=5)
        
        # ─── ОТКРЫТЬ ПРИЛОЖЕНИЕ ───
        elif action == "open_app":
            pkg = params.get("package", "")
            if not pkg:
                return "Не указан пакет, сэр."
            
            # Пробуем URL-схему
            url = URL_SCHEMES.get(pkg)
            if url:
                try:
                    subprocess.run(["termux-open", url],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                    return reply
                except:
                    pass
            
            # Пробуем найти Activity
            try:
                dump = subprocess.check_output(["dumpsys", "package", pkg],
                                             stderr=subprocess.DEVNULL, timeout=10).decode()
                match = re.search(r'android\.intent\.action\.MAIN.*?\n\s+\w+\s+\w+\s+[^ ]+/([^ ]+)', dump)
                if match:
                    activity = match.group(1)
                    subprocess.run(["am", "start", "-n", f"{pkg}/{activity}"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            except:
                pass
            
            return reply
        
        # ─── ГРОМКОСТЬ ───
        elif action == "set_volume":
            level = int(params.get("level", 7))
            level = max(1, min(15, level))  # Ограничиваем от 1 до 15
            subprocess.run(["termux-volume", "music", str(level)], timeout=5)
        
        # ─── БУФЕР ОБМЕНА ───
        elif action == "clipboard":
            text = params.get("text", "")
            subprocess.run(["termux-clipboard-set", text], timeout=5)
        
        # ─── УВЕДОМЛЕНИЕ ───
        elif action == "notification":
            title = params.get("title", "Джарвис")
            message = params.get("message", "")
            subprocess.run(["termux-notification", "--title", title, "--content", message], timeout=5)
        
        # ─── ПОИСК В ИНТЕРНЕТЕ ───
        elif action == "search_web":
            query = params.get("query", "")
            encoded_query = urllib.parse.quote(query)
            subprocess.run(["termux-open", f"https://google.com/search?q={encoded_query}"], timeout=5)
        
        # ─── МУЗЫКА ───
        elif action == "play_music":
            artist = params.get("artist", "")
            encoded_artist = urllib.parse.quote(artist)
            subprocess.run(["termux-open", f"https://music.youtube.com/search?q={encoded_artist}"], timeout=5)
        
        # ─── ИНФОРМАЦИЯ О СИСТЕМЕ ───
        elif action == "system_info":
            try:
                # Батарея
                battery_json = subprocess.check_output(["termux-battery-status"], timeout=5).decode()
                battery = json.loads(battery_json)
                
                # Память
                storage = subprocess.check_output(["df", "-h", "/sdcard"], timeout=5).decode()
                
                reply = f"🔋 Батарея: {battery.get('percentage', '?')}%, {battery.get('status', 'unknown')}\n"
                reply += f"💾 Память:\n{storage}"
            except Exception as e:
                reply = f"Не удалось получить информацию: {e}"
        
        # ─── ВРЕМЯ ───
        elif action == "say_time":
            now = datetime.now().strftime("%H:%M")
            reply = f"Сейчас {now}, сэр."
        
        # ─── БЛОКИРОВКА ЭКРАНА ───
        elif action == "lock_screen":
            subprocess.run(["input", "keyevent", "26"], timeout=5)
        
        # ─── СКРИНШОТ ───
        elif action == "screenshot":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/sdcard/screenshot_{timestamp}.png"
            result = subprocess.run(["/system/bin/screencap", "-p", filename], 
                                  timeout=5, capture_output=True)
            if result.returncode == 0:
                reply = f"Скриншот сохранён: {filename}, сэр."
            else:
                reply = "Не удалось сделать скриншот, сэр."
        
        return reply
    
    except json.JSONDecodeError as e:
        return f"Ошибка парсинга JSON: {e}\nОтвет модели: {action_json[:200]}"
    except subprocess.TimeoutExpired:
        return "Команда выполнялась слишком долго, сэр."
    except Exception as e:
        return f"Ошибка: {e}"

# ─── ОСНОВНОЙ ЦИКЛ ───
def main():
    print("=" * 50)
    print("  🤖 ДЖАРВИС — УПРАВЛЕНИЕ ТЕЛЕФОНОМ")
    print("  Команды: /выход")
    print("  Что умею:")
    print("  • Открывать приложения")
    print("  • Включать/выключать фонарик")
    print("  • Управлять громкостью")
    print("  • Копировать текст в буфер")
    print("  • Показывать уведомления")
    print("  • Искать в интернете")
    print("  • Показывать время")
    print("  • Информация о системе")
    print("  • Блокировка экрана")
    print("  • Скриншоты")
    print("=" * 50)
    
    while True:
        try:
            user = input("\n📝 Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not user:
            continue
        if user.lower() == "/выход":
            print("👋 До свидания, сэр.")
            break
        
        print("🧠 Думаю...")
        response = ask_jarvis(user)
        
        if response:
            result = execute_action(response)
            print(f"🤖 Джарвис: {result}")
        else:
            print("🤖 Джарвис: Прошу прощения, сэр. Связь с ядром потеряна.")

if __name__ == "__main__":
    main()
