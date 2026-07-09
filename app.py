from chatbot.chatbot import ChatBot


def main():
    print("=" * 40)
    print("🤖 AI Workspace")
    print("输入 exit 退出")
    print("=" * 40)

    bot = ChatBot()

    while True:
        user_input = input("\n你：")

        if user_input.lower() == "exit":
            print("AI：再见，祝你学习顺利！")
            break

        answer = bot.reply(user_input)
        print(f"AI：{answer}")


if __name__ == "__main__":
    main()