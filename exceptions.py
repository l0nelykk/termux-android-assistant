# exceptions.py
"""Пользовательские исключения для ассистента"""


class AssistantError(Exception):
    """Базовое исключение ассистента"""
    pass


class OllamaConnectionError(AssistantError):
    """Ошибка подключения к Ollama"""
    def __init__(self, message: str, original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(message)


class InvalidCommandFormatError(AssistantError):
    """Некорректный формат JSON от модели"""
    def __init__(self, raw_response: str, parse_error: str):
        self.raw_response = raw_response
        self.parse_error = parse_error
        super().__init__(f"Невалидный JSON от модели: {parse_error}")


class CommandExecutionError(AssistantError):
    """Ошибка при выполнении команды"""
    def __init__(self, command_name: str, reason: str, original_error: Exception | None = None):
        self.command_name = command_name
        self.reason = reason
        self.original_error = original_error
        super().__init__(f"Ошибка выполнения команды '{command_name}': {reason}")
