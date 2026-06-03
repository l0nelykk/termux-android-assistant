# commands/implementations.py
"""Реализация конкретных команд"""
import subprocess
import json
import urllib.parse
import re
from datetime import datetime
from typing import Any

from commands.base import Command, CommandMetadata


class FlashlightOnCommand(Command):
    @property
    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="flashlight_on",
            description="включить фонарик на телефоне"
        )
    
    def execute(self, params: dict[str, Any]) -> str:
        try:
            subprocess.run(["termux-torch", "on"], timeout=5, check=True)
            return "Фонарик включён"
        except subprocess.TimeoutExpired:
            return "Ошибка: команда фонарика не завершилась за 5 секунд"
        except FileNotFoundError:
            return "Ошибка: termux-torch не установлен"
        except subprocess.CalledProcessError as e:
            return f"Ошибка выполнения: {e}"


class FlashlightOffCommand(Command):
    @property
    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="flashlight_off",
            description="выключить фонарик на телефоне"
        )
    
    def execute(self, params: dict[str, Any]) -> str:
        try:
            subprocess.run(["termux-torch", "off"], timeout=5, check=True)
            return "Фонарик выключен"
        except subprocess.TimeoutExpired:
            return "Ошибка: команда фонарика не завершилась за 5 секунд"
        except FileNotFoundError:
            return "Ошибка: termux-torch не установлен"
        except subprocess.CalledProcessError as e:
            return f"Ошибка выполнения: {e}"


class SetVolumeCommand(Command):
    @property
    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="set_volume",
            description="установить громкость музыки (от 1 до 15)",
            param_schema={"level": {"type": "integer", "min": 1, "max": 15}}
        )
    
    def execute(self, params: dict[str, Any]) -> str:
        try:
            level = int(params.get("level", 7))
            level = max(1, min(15, level))
            subprocess.run(["termux-volume", "music", str(level)], timeout=5, check=True)
            return f"Громкость установлена на {level}"
        except (ValueError, TypeError):
            return "Ошибка: уровень громкости должен быть числом"
        except subprocess.TimeoutExpired:
            return "Ошибка: команда не завершилась за 5 секунд"
        except FileNotFoundError:
            return "Ошибка: termux-volume не установлен"


class ClipboardCommand(Command):
    @property
    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="clipboard",
            description="скопировать текст в буфер обмена",
            param_schema={"text": {"type": "string"}}
        )
    
    def execute(self, params: dict[str, Any]) -> str:
        try:
            text = params.get("text", "")
            subprocess.run(["termux-clipboard-set", text], timeout=5, check=True)
            preview = text[:50] + "..." if len(text) > 50 else text
            return f"Текст скопирован: {preview}"
        except subprocess.TimeoutExpired:
            return "Ошибка: команда не завершилась за 5 секунд"
        except FileNotFoundError:
            return "Ошибка: termux-clipboard-set не установлен"


class NotificationCommand(Command):
    @property
    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="notification",
            description="показать уведомление",
            param_schema={"title": {"type": "string"}, "message": {"type": "string"}}
        )
    
    def execute(self, params: dict[str, Any]) -> str:
        try:
            title = params.get("title", "Ассистент")
            message = params.get("message", "")
            subprocess.run(["termux-notification", "--title", title, "--content", message], timeout=5, check=True)
            return f"Уведомление: {title}"
        except subprocess.TimeoutExpired:
            return "Ошибка: команда не завершилась за 5 секунд"
        except FileNotFoundError:
            return "Ошибка: termux-notification не установлен"


class SearchWebCommand(Command):
    @property
    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="search_web",
            description="выполнить поиск в интернете через Google",
            param_schema={"query": {"type": "string"}}
        )
    
    def execute(self, params: dict[str, Any]) -> str:
        try:
            query = params.get("query", "")
            encoded_query = urllib.parse.quote(query)
            subprocess.run(["termux-open", f"https://google.com/search?q={encoded_query}"], timeout=5, check=True)
            return f"Поиск: {query}"
        except subprocess.TimeoutExpired:
            return "Ошибка: команда не завершилась за 5 секунд"
        except FileNotFoundError:
            return "Ошибка: termux-open не установлен"


class PlayMusicCommand(Command):
    @property
    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="play_music",
            description="включить музыку на YouTube Music",
            param_schema={"artist": {"type": "string"}}
        )
    
    def execute(self, params: dict[str, Any]) -> str:
        try:
            artist = params.get("artist", "")
            encoded_artist = urllib.parse.quote(artist)
            subprocess.run(["termux-open", f"https://music.youtube.com/search?q={encoded_artist}"], timeout=5, check=True)
            return f"Включаю музыку: {artist}"
        except subprocess.TimeoutExpired:
            return "Ошибка: команда не завершилась за 5 секунд"
        except FileNotFoundError:
            return "Ошибка: termux-open не установлен"


class SayTimeCommand(Command):
    @property
    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="say_time",
            description="сказать текущее время"
        )
    
    def execute(self, params: dict[str, Any]) -> str:
        now = datetime.now().strftime("%H:%M")
        return f"Сейчас {now}"


class SystemInfoCommand(Command):
    @property
    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="system_info",
            description="показать информацию о батарее и памяти телефона"
        )
    
    def execute(self, params: dict[str, Any]) -> str:
        try:
            battery_json = subprocess.check_output(["termux-battery-status"], timeout=5).decode()
            battery = json.loads(battery_json)
            storage = subprocess.check_output(["df", "-h", "/sdcard"], timeout=5).decode()
            result = f"Батарея: {battery.get('percentage', '?')}%, {battery.get('status', 'unknown')}\n"
            result += f"Память:\n{storage}"
            return result
        except subprocess.TimeoutExpired:
            return "Ошибка: команда не завершилась за 5 секунд"
        except FileNotFoundError as e:
            return f"Ошибка: {e.filename} не найден"
        except json.JSONDecodeError as e:
            return f"Ошибка парсинга данных батареи: {e}"
        except Exception as e:
            return f"Не удалось получить информацию: {type(e).__name__}: {e}"


class LockScreenCommand(Command):
    @property
    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="lock_screen",
            description="заблокировать экран телефона"
        )
    
    def execute(self, params: dict[str, Any]) -> str:
        try:
            subprocess.run(["input", "keyevent", "26"], timeout=5, check=True)
            return "Экран заблокирован"
        except subprocess.TimeoutExpired:
            return "Ошибка: команда не завершилась за 5 секунд"
        except FileNotFoundError:
            return "Ошибка: команда 'input' не найдена"
        except subprocess.CalledProcessError as e:
            return f"Ошибка блокировки экрана: {e}"


class ScreenshotCommand(Command):
    @property
    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="screenshot",
            description="сделать скриншот экрана"
        )
    
    def execute(self, params: dict[str, Any]) -> str:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/sdcard/screenshot_{timestamp}.png"
            result = subprocess.run(["/system/bin/screencap", "-p", filename], timeout=5, capture_output=True)
            if result.returncode == 0:
                return f"Скриншот сохранён: {filename}"
            else:
                return f"Не удалось сделать скриншот: {result.stderr.decode()[:200]}"
        except subprocess.TimeoutExpired:
            return "Ошибка: команда не завершилась за 5 секунд"
        except FileNotFoundError:
            return "Ошибка: screencap не найден"


class OpenAppCommand(Command):
    @property
    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="open_app",
            description="открыть приложение на телефоне",
            param_schema={"app_name": {"type": "string"}}
        )
    
    def _get_all_packages(self) -> list[str]:
        """Возвращает список всех установленных пакетов"""
        try:
            result = subprocess.run(["pm", "list", "packages"], capture_output=True, text=True, timeout=10)
            packages = [line.replace("package:", "").strip() for line in result.stdout.splitlines()]
            return packages
        except Exception:
            return []
    
    def _find_package_by_app_name(self, app_name: str) -> str | None:
        """Улучшенный поиск пакета по названию"""
        packages = self._get_all_packages()
        app_name_lower = app_name.lower().replace("-", " ").replace("_", " ")
        
        # Специальные соответствия (популярные приложения)
        special = {
            "тик ток": "com.zhiliaoapp.musically",
            "тикток": "com.zhiliaoapp.musically",
            "tiktok": "com.zhiliaoapp.musically",
            "яндекс музыка": "com.yandex.music",
            "ютуб": "com.google.android.youtube",
            "youtube": "com.google.android.youtube",
            "спотифай": "com.spotify.music",
            "spotify": "com.spotify.music",
            "телеграм": "org.telegram.messenger",
            "telegram": "org.telegram.messenger",
            "вк": "com.vkontakte.android",
            "vk": "com.vkontakte.android",
            "гугл": "com.android.chrome",
            "google": "com.android.chrome",
            "хром": "com.android.chrome",
            "chrome": "com.android.chrome",
            "калькулятор": "com.google.android.calculator",
            "настройки": "com.android.settings",
            "settings": "com.android.settings",
            "камера": "com.android.camera",
            "camera": "com.android.camera",
            "галерея": "com.android.gallery3d",
            "gallery": "com.android.gallery3d",
        }
        
        # Проверяем специальные соответствия
        for key, pkg in special.items():
            if key in app_name_lower or app_name_lower in key:
                return pkg
        
        # Ищем среди установленных пакетов
        best_match = None
        best_score = 0
        
        for pkg in packages:
            short_name = pkg.split(".")[-1].lower()
            clean_short = re.sub(r'[0-9]', '', short_name)
            
            if app_name_lower in short_name or short_name in app_name_lower:
                return pkg
            
            score = 0
            for word in app_name_lower.split():
                if word in short_name:
                    score += len(word)
                if short_name in word:
                    score += len(short_name)
            
            if score > best_score:
                best_score = score
                best_match = pkg
        
        if best_score > 2:
            return best_match
        
        return None
    
    def execute(self, params: dict[str, Any]) -> str:
        app_name = params.get("app_name", "")
        
        if not app_name:
            return "Ошибка: не указано название приложения"
        
        package = self._find_package_by_app_name(app_name)
        
        if not package:
            clean_name = re.sub(r'[^\w\s]', '', app_name).lower()
            package = self._find_package_by_app_name(clean_name)
            if not package:
                return f"Не удалось найти приложение: {app_name}"
        
        # Попытка открыть через известные URL схемы
        url_schemes = {
            "com.google.android.youtube": "vnd.youtube://",
            "com.android.chrome": "https://google.com",
            "com.google.android.calculator": "calculator://",
            "com.android.settings": "settings://",
            "com.android.dialer": "tel://",
            "com.android.camera": "camera://",
            "com.spotify.music": "spotify://",
            "com.termux": "termux://",
            "com.yandex.music": "yandexmusic://",
            "com.zhiliaoapp.musically": "snssdk1128://",
        }
        
        url = url_schemes.get(package)
        if url:
            try:
                subprocess.run(["termux-open", url], capture_output=True, timeout=5)
                return f"Открываю приложение: {app_name}"
            except Exception:
                pass
        
        # Пробуем найти Activity через dumpsys
        try:
            dump = subprocess.check_output(["dumpsys", "package", package], stderr=subprocess.DEVNULL, timeout=10).decode()
            match = re.search(r'android\.intent\.action\.MAIN.*?\n\s+\w+\s+\w+\s+[^ ]+/([^ ]+)', dump, re.DOTALL)
            if match:
                activity = match.group(1)
                subprocess.run(["am", "start", "-n", f"{package}/{activity}"], capture_output=True, timeout=5)
                return f"Открываю приложение: {app_name}"
        except Exception:
            pass
        
        # Пробуем через monkey
        try:
            subprocess.run(["monkey", "-p", package, "1"], capture_output=True, timeout=5)
            return f"Пытаюсь открыть: {app_name}"
        except Exception:
            pass
        
        return f"Не удалось открыть приложение: {app_name}"
