# core.py
import subprocess
import json
from datetime import datetime
from typing import List

from commands.base import Command
from commands.implementations import (
    FlashlightOnCommand,
    FlashlightOffCommand,
    SetVolumeCommand,
    ClipboardCommand,
    NotificationCommand,
    SearchWebCommand,
    PlayMusicCommand,
    SayTimeCommand,
    SystemInfoCommand,
    LockScreenCommand,
    ScreenshotCommand,
    OpenAppCommand,
)
from ollama_client import OllamaClient
from models import ModelResponse
from exceptions import InvalidCommandFormatError, OllamaConnectionError


class AssistantCore:
    def __init__(self, model: str = "qwen2.5:1.5b"):
        self.commands: List[Command] = []
        self._register_commands()
        self.ollama = OllamaClient(model=model)
    
    def _register_commands(self):
        self.commands = [
            FlashlightOnCommand(),
            FlashlightOffCommand(),
            SetVolumeCommand(),
            ClipboardCommand(),
            NotificationCommand(),
            SearchWebCommand(),
            PlayMusicCommand(),
            SayTimeCommand(),
            SystemInfoCommand(),
            LockScreenCommand(),
            ScreenshotCommand(),
            OpenAppCommand(),
        ]
    
    def _build_system_prompt(self) -> str:
        actions_list = "\n".join([cmd.metadata.name for cmd in self.commands])
        
        return f"""Ты — Джарвис, AI-ассистент с доступом к Android.
Ты можешь выполнять команды на телефоне.

На любую просьбу ты ОБЯЗАН вернуть ТОЛЬКО JSON, ничего больше.

Доступные команды: {actions_list}

Для команды open_app используй параметр app_name с названием приложения, которое хочет открыть пользователь. Не нужно угадывать package, просто передай название.

Формат ответа строго:
{{"action": "название_команды", "params": {{"параметр": "значение"}}, "reply": "что сказать пользователю"}}

Примеры:
"включи фонарик" -> {{"action": "flashlight_on", "params": {{}}, "reply": "Фонарик включён"}}
"открой ютуб" -> {{"action": "open_app", "params": {{"app_name": "ютуб"}}, "reply": "Открываю YouTube"}}
"открой калькулятор" -> {{"action": "open_app", "params": {{"app_name": "калькулятор"}}, "reply": "Открываю калькулятор"}}
"установи громкость на 10" -> {{"action": "set_volume", "params": {{"level": 10}}, "reply": "Громкость установлена"}}
"который час" -> {{"action": "say_time", "params": {{}}, "reply": "Сейчас 14:30"}}
"""
    
    def _find_command(self, action_name: str):
        for cmd in self.commands:
            if cmd.metadata.name == action_name:
                return cmd
        return None
    
    def process(self, user_input: str) -> str:
        print("Думаю...")
        
        system_prompt = self._build_system_prompt()
        full_prompt = f"{system_prompt}\n\nПользователь: {user_input}\nДжарвис:"
        
        try:
            response = self.ollama.generate(full_prompt)
            print(f"[DEBUG] Ответ модели: {response.raw_json}")
        except InvalidCommandFormatError as e:
            return f"Ошибка формата JSON: {e.parse_error}\nОтвет: {e.raw_response[:200]}"
        except OllamaConnectionError as e:
            return f"Ошибка подключения к Ollama: {e}"
        
        command = self._find_command(response.action)
        if not command:
            return f"{response.reply}\nНеизвестная команда: {response.action}"
        
        try:
            result = command.execute(response.params)
            return f"{response.reply}\n{result}"
        except Exception as e:
            return f"{response.reply}\nОшибка выполнения: {e}"
