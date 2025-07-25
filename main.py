import os
from flask import Flask, request
from telebot import TeleBot, types

TOKEN = '7561769200:AAEbeAAAZLFAoO7WrnQgYpZ3jz3lOfHYRjQ'
bot = TeleBot(TOKEN)
app = Flask(__name__)

WEBHOOK_URL_BASE = 'https://telegram-bot-l2vg.onrender.com'  # заменишь на свой URL
WEBHOOK_URL_PATH = f'/bot{TOKEN}'

user_state = {}

def get_back_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('↩️ Назад'))
    return keyboard

def step_start(message):
    user_state[message.chat.id] = 'start'

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text='🖥️ Регистрация',
        url='https://pocketoption.com/ru/?c=DEV906'
    ))
    markup.add(types.InlineKeyboardButton(
        text='✅ Я зарегистрировался',
        callback_data='registered'
    ))

    text = (
        'Привет! 👋\n\n'
        '📲Чтобы получить доступ к приватному каналу, тебе необходимо стать моим партнёром на Pocket Option и пройти регистрацию. '
        'Чтобы бот успешно проверил регистрацию, нужно соблюсти важные условия:\n\n'
        '1️⃣ Аккаунт обязательно должен быть **НОВЫМ**! Если у вас уже есть аккаунт и при нажатии на кнопку "РЕГИСТРАЦИЯ" '
        'вы попадаете на старый, необходимо выйти с него и заново нажать на кнопку "РЕГИСТРАЦИЯ", после чего по новой зарегистрироваться!\n\n'
        '2️⃣ Чтобы бот смог проверить вашу регистрацию, обязательно нужно ввести промокод **DEV906** при регистрации! '
        'Он также дополнительно даёт +60% к пополнению!\n\n'
        'После РЕГИСТРАЦИИ бот автоматически переведёт вас к следующему шагу ✅'
    )

    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

def step_enter_id(message):
    user_state[message.chat.id] = 'enter_id'
    bot.send_message(
        message.chat.id,
        '✅ Введите ID (только цифры):',
        reply_markup=get_back_keyboard()
    )

@bot.message_handler(commands=['start'])
def handle_start(message):
    step_start(message)

@bot.callback_query_handler(func=lambda call: call.data == 'registered')
def handle_registered_callback(call):
    bot.answer_callback_query(call.id)
    step_enter_id(call.message)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if text == '↩️ Назад':
        current = user_state.get(chat_id, 'start')
        if current == 'enter_id':
            step_start(message)
        else:
            bot.send_message(chat_id, "Вы уже на начальном шаге 👇", reply_markup=get_back_keyboard())
        return

    if user_state.get(chat_id) == 'enter_id':
        if text.isdigit():
            bot.send_message(chat_id, f'📩 Ваш ID "{text}" получен и отправлен на проверку!', reply_markup=get_back_keyboard())
        else:
            bot.send_message(chat_id, '❗ Пожалуйста, введите только цифры для ID.', reply_markup=get_back_keyboard())
        return

    bot.send_message(chat_id, '❗ Некорректная команда 🙁', reply_markup=get_back_keyboard())

# ======== WEBHOOK PART =========

@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# Установка вебхука при старте
@app.before_first_request
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))