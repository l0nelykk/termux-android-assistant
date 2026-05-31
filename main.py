from core import ask_jarvis, execute_action

def main():
    print("=" * 50)
    print("  ДЖАРВИС — УПРАВЛЕНИЕ ТЕЛЕФОНОМ")
    print("  Команды: /выход")
    print("=" * 50)

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

        print("Думаю...")
        response = ask_jarvis(user)

        if response:
            result = execute_action(response)
            print(f"Джарвис: {result}")
        else:
            print("Джарвис: Прошу прощения, связь с ядром потеряна.")

if __name__ == "__main__":
    main()
