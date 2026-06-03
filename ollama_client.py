# ollama_client.py
"""Клиент для работы с Ollama API"""
import json
import requests
from typing import Any
from datetime import datetime

from exceptions import OllamaConnectionError, InvalidCommandFormatError
from models import ModelResponse


class OllamaClient:
    """Клиент для взаимодействия с языковой моделью"""
    
    def __init__(self, model: str = "qwen2.5:1.5b", base_url: str = "http://127.0.0.1:11434"):
        self.model = model
        self.generate_url = f"{base_url}/api/generate"
        self.timeout: int = 30
    
    def generate(self, prompt: str) -> ModelResponse:
        """Отправляет запрос модели и возвращает структурированный ответ"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=self.timeout
            )
        except requests.exceptions.ConnectionError as e:
            raise OllamaConnectionError(
                f"Не удалось подключиться к Ollama на {self.generate_url}. Убедитесь, что Ollama запущена.",
                original_error=e
            )
        except requests.exceptions.Timeout as e:
            raise OllamaConnectionError(
                f"Таймаут подключения к Ollama после {self.timeout} секунд.",
                original_error=e
            )
        except Exception as e:
            raise OllamaConnectionError(
                f"Неизвестная ошибка при подключении к Ollama: {type(e).__name__}",
                original_error=e
            )
        
        if response.status_code != 200:
            raise OllamaConnectionError(
                f"Ollama вернула код ошибки {response.status_code}: {response.text[:200]}"
            )
        
        # Парсим JSON ответ Ollama
        try:
            response_data = response.json()
            raw_response = response_data.get("response", "").strip()
        except json.JSONDecodeError as e:
            raise InvalidCommandFormatError(
                raw_response=response.text[:500],
                parse_error=f"Невалидный JSON от Ollama: {e}"
            )
        
        # Парсим JSON команды от модели
        try:
            command_data = json.loads(raw_response)
        except json.JSONDecodeError as e:
            raise InvalidCommandFormatError(
                raw_response=raw_response[:500],
                parse_error=f"Модель вернула невалидный JSON: {e}"
            )
        
        # Валидируем структуру
        if "action" not in command_data:
            raise InvalidCommandFormatError(
                raw_response=raw_response[:500],
                parse_error="Отсутствует обязательное поле 'action' в JSON"
            )
        
        return ModelResponse(
            action=command_data["action"],
            params=command_data.get("params", {}),
            reply=command_data.get("reply", "Выполняю команду"),
            raw_json=raw_response
        )
