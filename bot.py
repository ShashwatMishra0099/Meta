import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram_login import TelegramLogin

# Use environment variables for sensitive information
API_TOKEN = os.getenv('API_TOKEN')
GITHUB_REPO_URL = os.getenv('GITHUB_REPO_URL')
GROUP_ID = os.getenv('GROUP_ID')

telegram_login = TelegramLogin(api_id=os.getenv('API_ID'), api_hash=os.getenv('API_HASH'))  # Example, adjust as necessary

def start(update, context):
    try:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please enter your phone number to log in.')
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Error: {str(e)}')

def login(update, context):
    phone_number = update.message.text
    try:
        otp_sent = telegram_login.send_otp(phone_number)
        if otp_sent:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Please enter the OTP sent to your phone.')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Failed to send OTP.')
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Error: {str(e)}')

def otp_input(update, context):
    otp = update.message.text
    try:
        login_success = telegram_login.verify_otp(otp)
        if login_success:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Login successful!')
            add_members(update, context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Invalid OTP.')
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Error: {str(e)}')

def add_members(update, context):
    try:
        members_file = os.path.join(GITHUB_REPO_URL, 'members.txt')
        with open(members_file, 'r') as f:
            members = [line.strip() for line in f.readlines()]

        bot = telegram.Bot(token=API_TOKEN)
        for member in members:
            bot.add_chat_member(GROUP_ID, member)
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Error: {str(e)}')

def main():
    updater = Updater(API_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, login))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, otp_input))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
