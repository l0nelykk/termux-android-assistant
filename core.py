import requests
import json

MODEL = "qwen2.5:1.5b"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def build_system_prompt():
    """Собирает промпт из списка действий"""
    from commands import ACTIONS_REGISTRY
    
    actions_list = "\n".join(ACTIONS_REGISTRY.keys())
    
    return f"""Ты — Джарвис, AI-ассистент с доступом к Android.
Ты можешь выполнять команды на телефоне.

На любую просьбу ты ОБЯЗАН вернуть ТОЛЬКО JSON, ничего больше.

Доступные команды: {actions_list}

Формат ответа строго:
{{"action": "название_команды", "params": {{"параметр": "значение"}}, "reply": "что сказать пользователю"}}

Примеры:
"включи фонарик" -> {{"action": "flashlight_on", "params": {{}}, "reply": "Фонарик включён"}}
"установи громкость на 10" -> {{"action": "set_volume", "params": {{"level": 10}}, "reply": "Громкость установлена"}}
"который час" -> {{"action": "say_time", "params": {{}}, "reply": "Сейчас 14:30"}}
"""

def ask_jarvis(user_input):
    """Отправляет запрос модели, возвращает JSON-строку"""
    system_prompt = build_system_prompt()
    prompt = f"{system_prompt}\n\nПользователь: {user_input}\nДжарвис:"

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if resp.status_code == 200:
            response_text = resp.json()["response"].strip()
            return response_text
    except Exception as e:
        print(f"Ошибка подключения к Ollama: {e}")
    return None

def execute_action(action_json):
    """Получает JSON от модели, вызывает нужную функцию"""
    try:
        data = json.loads(action_json)
        action = data.get("action")
        params = data.get("params", {})
        reply = data.get("reply", "Сделано.")

        if not action:
            return reply

        print(f"Выполняю: {action}")

        from commands import ACTIONS_REGISTRY
        
        if action in ACTIONS_REGISTRY:
            result = ACTIONS_REGISTRY[action](params)
            return f"{reply}\n{result}"
        else:
            return f"Неизвестное действие: {action}"

    except json.JSONDecodeError as e:
        return f"Ошибка парсинга JSON: {e}\nОтвет модели: {action_json[:200]}"
    except Exception as e:
        return f"Ошибка: {e}"
