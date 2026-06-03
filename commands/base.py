# commands/base.py
"""Базовые классы для команд"""
from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CommandMetadata:
    """Метаданные команды"""
    name: str
    description: str
    param_schema: dict[str, Any] = field(default_factory=dict)


class Command(ABC):
    """Абстрактный базовый класс для всех команд"""
    
    @property
    @abstractmethod
    def metadata(self) -> CommandMetadata:
        """Возвращает метаданные команды"""
        pass
    
    @abstractmethod
    def execute(self, params: dict[str, Any]) -> str:
        """Выполняет команду и возвращает результат"""
        pass
    
    def get_prompt_description(self) -> str:
        """Возвращает описание команды для системного промпта"""
        return f"- {self.metadata.name}: {self.metadata.description}"
