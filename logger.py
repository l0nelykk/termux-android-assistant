# logger.py
"""JSON-логирование с ротацией"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from threading import Lock


class JsonLogger:
    """Логгер с автоматической ротацией по дням"""
    
    def __init__(self, log_dir: str = "logs", max_size_mb: int = 10):
        self.log_dir = Path(log_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self._current_date = None
        self._file_handle = None
        self._lock = Lock()
        self._ensure_log_dir()
    
    def _ensure_log_dir(self) -> None:
        """Создаёт директорию для логов если её нет"""
        self.log_dir.mkdir(exist_ok=True)
    
    def _get_log_path(self) -> Path:
        """Возвращает путь к файлу лога для текущей даты"""
        today = datetime.now().strftime("%Y%m%d")
        return self.log_dir / f"assistant_{today}.json"
    
    def _rotate_if_needed(self, log_path: Path) -> None:
        """Проверяет размер файла и выполняет ротацию при необходимости"""
        if log_path.exists() and log_path.stat().st_size > self.max_size_bytes:
            # Создаём архивный файл с timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = self.log_dir / f"assistant_{timestamp}_archived.json"
            log_path.rename(archive_path)
    
    def _open_log_file(self):
        """Открывает файл лога для текущей даты"""
        log_path = self._get_log_path()
        self._rotate_if_needed(log_path)
        
        # Определяем, нужно ли писать запятую перед новой записью
        need_comma = log_path.exists() and log_path.stat().st_size > 0
        
        # Открываем файл в режиме добавления
        self._file_handle = open(log_path, 'a', encoding='utf-8')
        
        # Если файл пустой, начинаем массив JSON
        if not need_comma:
            self._file_handle.write('[\n')
        else:
            self._file_handle.write(',\n')
        
        return need_comma
    
    def log(self, entry: dict[str, Any]) -> None:
        """Записывает запись в лог"""
        with self._lock:
            try:
                # Определяем, нужно ли писать запятую
                log_path = self._get_log_path()
                need_comma = log_path.exists() and log_path.stat().st_size > 0
                
                with open(log_path, 'a', encoding='utf-8') as f:
                    if not need_comma:
                        f.write('[\n')
                    
                    json.dump(entry, f, ensure_ascii=False, indent=2)
                    f.write('\n')
            except Exception as e:
                # Логируем в stderr, так как основной логгер недоступен
                import sys
                print(f"Ошибка записи лога: {e}", file=sys.stderr)
    
    def close(self):
        """Закрывает файл лога корректно"""
        with self._lock:
            if self._file_handle:
                # Закрываем массив JSON
                self._file_handle.write('\n]')
                self._file_handle.close()
                self._file_handle = None
