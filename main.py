# main.py
from core import AssistantCore

def main():
    print("=" * 50)
    print("  ДЖАРВИС — УПРАВЛЕНИЕ ТЕЛЕФОНОМ")
    print("  Команды: /выход")
    print("=" * 50)
    
    assistant = AssistantCore()
    
    while True:
        try:
            user = input("\nВы: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not user:
            continue
        
        if user.lower() == "/выход":
            print("До свидания.")
            break
        
        result = assistant.process(user)
        print(f"Джарвис: {result}")

if __name__ == "__main__":
    main()
