import subprocess
import json
from datetime import datetime

def action_flashlight_on(params):
    subprocess.run(["termux-torch", "on"], timeout=5)
    return "Фонарик включён"

def action_flashlight_off(params):
    subprocess.run(["termux-torch", "off"], timeout=5)
    return "Фонарик выключен"

def action_set_volume(params):
    level = int(params.get("level", 7))
    level = max(1, min(15, level))
    subprocess.run(["termux-volume", "music", str(level)], timeout=5)
    return f"Громкость установлена на {level}"

def action_clipboard(params):
    text = params.get("text", "")
    subprocess.run(["termux-clipboard-set", text], timeout=5)
    return f"Текст скопирован: {text[:50]}"

def action_notification(params):
    title = params.get("title", "Джарвис")
    message = params.get("message", "")
    subprocess.run(["termux-notification", "--title", title, "--content", message], timeout=5)
    return f"Уведомление: {title}"

def action_search_web(params):
    import urllib.parse
    query = params.get("query", "")
    encoded_query = urllib.parse.quote(query)
    subprocess.run(["termux-open", f"https://google.com/search?q={encoded_query}"], timeout=5)
    return f"Поиск: {query}"

def action_play_music(params):
    import urllib.parse
    artist = params.get("artist", "")
    encoded_artist = urllib.parse.quote(artist)
    subprocess.run(["termux-open", f"https://music.youtube.com/search?q={encoded_artist}"], timeout=5)
    return f"Включаю музыку: {artist}"

def action_say_time(params):
    now = datetime.now().strftime("%H:%M")
    return f"Сейчас {now}"

def action_system_info(params):
    try:
        battery_json = subprocess.check_output(["termux-battery-status"], timeout=5).decode()
        battery = json.loads(battery_json)
        storage = subprocess.check_output(["df", "-h", "/sdcard"], timeout=5).decode()
        result = f"Батарея: {battery.get('percentage', '?')}%, {battery.get('status', 'unknown')}\n"
        result += f"Память:\n{storage}"
        return result
    except Exception as e:
        return f"Не удалось получить информацию: {e}"

def action_lock_screen(params):
    subprocess.run(["input", "keyevent", "26"], timeout=5)
    return "Экран заблокирован"

def action_screenshot(params):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/sdcard/screenshot_{timestamp}.png"
    result = subprocess.run(["/system/bin/screencap", "-p", filename], timeout=5, capture_output=True)
    if result.returncode == 0:
        return f"Скриншот сохранён: {filename}"
    else:
        return "Не удалось сделать скриншот"

def action_open_app(params):
    pkg = params.get("package", "")
    if not pkg:
        return "Не указан пакет"
    
    import re
    # Пробуем URL-схему
    URL_SCHEMES = {
        "com.google.android.youtube": "vnd.youtube://",
        "com.android.chrome": "https://google.com",
        "com.google.android.calculator": "calculator://",
        "com.android.settings": "settings://",
        "com.android.dialer": "tel://",
        "com.android.camera": "camera://",
        "com.spotify.music": "spotify://",
        "com.termux": "termux://",
    }
    
    url = URL_SCHEMES.get(pkg)
    if url:
        try:
            subprocess.run(["termux-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            return f"Открываю приложение: {pkg}"
        except:
            pass
    
    # Пробуем найти Activity
    try:
        dump = subprocess.check_output(["dumpsys", "package", pkg], stderr=subprocess.DEVNULL, timeout=10).decode()
        match = re.search(r'android\.intent\.action\.MAIN.*?\n\s+\w+\s+\w+\s+[^ ]+/([^ ]+)', dump)
        if match:
            activity = match.group(1)
            subprocess.run(["am", "start", "-n", f"{pkg}/{activity}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            return f"Открываю приложение: {pkg}"
    except:
        pass
    
    return f"Не удалось открыть приложение: {pkg}"


# СЛОВАРЬ: связывает имена действий с функциями
ACTIONS_REGISTRY = {
    "flashlight_on": action_flashlight_on,
    "flashlight_off": action_flashlight_off,
    "set_volume": action_set_volume,
    "clipboard": action_clipboard,
    "notification": action_notification,
    "search_web": action_search_web,
    "play_music": action_play_music,
    "say_time": action_say_time,
    "system_info": action_system_info,
    "lock_screen": action_lock_screen,
    "screenshot": action_screenshot,
    "open_app": action_open_app,
}
