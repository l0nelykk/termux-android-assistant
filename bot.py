import requests
import json
import os
from datetime import datetime

# ─── НАСТРОЙКИ ───────────────────────────────
MODEL = "qwen2.5:1.5b"          # Модель
HISTORY_FILE = "memory.json"    # Файл памяти
MAX_HISTORY = 20                # Сколько последних сообщений помнить
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

# Системный промпт (характер)
SYSTEM_PROMPT = """Ты — Валерон, байкер из 90-х. 
Твои правила:
- Обращаешься к собеседнику "братан"
- Используешь слова: тема, зацени, по кайфу, тачка, мотор
- Если спрашивают про технологии — сводишь всё к карбюраторам
- Если спрашивают про отношения — даёшь советы в духе "бабы не главное, главное чтобы конь не подвёл"
- Ты добрый, но немного суровый. Матом не ругаешься, но крепкое словцо вставить можешь.
- В конце ответа иногда добавляешь "Понял, нет?"
"""

# ─── ФУНКЦИИ ──────────────────────────────────

def load_history():
    """Загружает историю диалога из файла"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    """Сохраняет историю диалога в файл"""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-MAX_HISTORY:], f, ensure_ascii=False, indent=2)

def chat(user_input, history):
    """Отправляет запрос в Ollama и возвращает ответ"""
    
    # Собираем полный промпт
    prompt = SYSTEM_PROMPT + "\n\n"
    
    # Добавляем историю диалога
    for msg in history[-MAX_HISTORY:]:
        prompt += f"Собеседник: {msg['user']}\nВалерон: {msg['bot']}\n"
    
    prompt += f"Собеседник: {user_input}\nВалерон:"
    
    # Запрос к Ollama
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.8,      # Креативность
            "top_p": 0.95,           # Разнообразие
            "repeat_penalty": 1.1    # Штраф за повторения
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            answer = response.json()["response"].strip()
            return answer
        else:
            return f"[Ошибка API: {response.status_code}]"
    except Exception as e:
        return f"[Ошибка соединения: {e}]"

# ─── ОСНОВНОЙ ЦИКЛ ────────────────────────────

def main():
    print("=" * 50)
    print("  ВАЛЕРОН — БАЙКЕР ИЗ 90-Х")
    print("  Команды: /выход, /очистить, /память")
    print("=" * 50)
    
    history = load_history()
    
    if history:
        print(f"\n[Загружено {len(history)} сообщений из памяти]")
    
    while True:
        try:
            user_input = input("\n📝 Ты: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not user_input:
            continue
        
        # Обработка команд
        if user_input == "/выход":
            save_history(history)
            print("👋 Бывай, братан! Заезжай если что!")
            break
        
        elif user_input == "/очистить":
            history = []
            save_history(history)
            print("🧹 Память очищена. Как с чистого листа.")
            continue
        
        elif user_input == "/память":
            if history:
                print(f"\n📚 Помню {len(history)} сообщений:")
                for i, msg in enumerate(history[-5:], 1):
                    print(f"  {i}. Ты: {msg['user'][:50]}...")
                    print(f"     Валерон: {msg['bot'][:50]}...")
            else:
                print("📚 Память пуста.")
            continue
        
        # Отправляем запрос
        print("⏳ Валерон думает...", end="\r")
        answer = chat(user_input, history)
        
        # Сохраняем в историю
        history.append({"user": user_input, "bot": answer, "time": datetime.now().strftime("%H:%M")})
        
        # Выводим ответ
        print(f"🏍️  Валерон: {answer}")
        
        # Автосохранение каждые 5 сообщений
        if len(history) % 5 == 0:
            save_history(history)

if __name__ == "__main__":
    main()
