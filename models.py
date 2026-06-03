# models.py
"""Иммутабельные модели данных"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class UserRequest:
    """Запрос пользователя"""
    text: str
    timestamp: datetime = datetime.now()


@dataclass(frozen=True)
class ModelResponse:
    """Ответ от языковой модели"""
    action: str
    params: dict[str, Any]
    reply: str
    raw_json: str
    timestamp: datetime = datetime.now()


@dataclass(frozen=True)
class ActionResult:
    """Результат выполнения команды"""
    success: bool
    message: str
    command_name: str
    error: str | None = None
    timestamp: datetime = datetime.now()


@dataclass(frozen=True)
class LogEntry:
    """Запись в лог"""
    event_type: str  # "request", "response", "execution", "error"
    data: dict[str, Any]
    timestamp: datetime = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }
