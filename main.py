import os
import sqlite3
from flask import Flask, request
from telebot import TeleBot, types
import requests

TOKEN = '7561769200:AAEbeAAAZLFAoO7WrnQgYpZ3jz3lOfHYRjQ'  # Токен
YOUR_DOMAIN = 'telegram-bot-l2vg.onrender.com'  # Заменить на свой домен
WEBHOOK_URL = f"https://{YOUR_DOMAIN}/{TOKEN}"

bot = TeleBot(TOKEN)
app = Flask(__name__)

user_state = {}

# Инициализация БД и таблицы
def init_db():
    conn = sqlite3.connect('botdata.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            trader_id TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# Сохраняем связь chat_id и trader_id
def save_user(chat_id, trader_id):
    conn = sqlite3.connect('botdata.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (chat_id, trader_id) VALUES (?, ?)', (chat_id, trader_id))
    conn.commit()
    conn.close()

# Получаем chat_id по trader_id
def get_chat_id_by_trader_id(trader_id):
    conn = sqlite3.connect('botdata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id FROM users WHERE trader_id = ?', (trader_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_start_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text='🖥️ Регистрация',
        url='https://u3.shortink.io/register?utm_campaign=823619&utm_source=affiliate&utm_medium=sr&a=gmURbwjR6oRBDh&ac=ttrade404&code=DEV906'  # Вставь свою ссылку
    ))
    markup.add(types.InlineKeyboardButton(
        text='✅ Я зарегистрировался',
        callback_data='registered'
    ))
    return markup

def get_back_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton('↩️ Назад'))
    return keyboard

def send_start_message(chat_id):
    user_state[chat_id] = 'start'
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
    bot.send_message(chat_id, text, reply_markup=get_start_keyboard(), parse_mode='Markdown')

def send_enter_id_message(chat_id):
    user_state[chat_id] = 'enter_id'
    bot.send_message(chat_id, "✅ Введите ID (только цифры):", reply_markup=get_back_keyboard())

def check_pocket_option_id(user_id):
    # Заглушка — просто проверяем, что это цифры и длина > 5
    return user_id.isdigit() and len(user_id) > 5

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

# Обработка postback от Pocket Option
@app.route('/postback', methods=['GET', 'POST'])
def postback():
    data = request.values
    trader_id = data.get('trader_id')
    reg = data.get('reg')
    ftd = data.get('ftd')

    if trader_id:
        chat_id = get_chat_id_by_trader_id(trader_id)
        if chat_id:
            if reg == '1':
                bot.send_message(chat_id, "✅ Поздравляем! Ваша регистрация подтверждена через партнёрку!")
            if ftd == '1':
                bot.send_message(chat_id, "💰 Поздравляем! Вы сделали первый депозит!")

    return 'OK', 200

@bot.message_handler(commands=['start'])
def handle_start(message):
    send_start_message(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == 'registered')
def handle_registered(call):
    bot.answer_callback_query(call.id)
    send_enter_id_message(call.message.chat.id)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if text == '↩️ Назад':
        send_start_message(chat_id)
        return

    if user_state.get(chat_id) == 'enter_id':
        if text.isdigit():
            if check_pocket_option_id(text):
                # Сохраняем соответствие chat_id <-> trader_id
                save_user(chat_id, text)
                bot.send_message(chat_id, f"✅ Ваш ID {text} успешно проверен и сохранён! Спасибо.", reply_markup=types.ReplyKeyboardRemove())
                user_state[chat_id] = 'verified'
            else:
                bot.send_message(chat_id, "❗ Ошибка❗ Некорректный ввод ID🙁 Попробуйте снова.", reply_markup=get_back_keyboard())
        else:
            bot.send_message(chat_id, "❗ Пожалуйста, введите только цифры для ID.", reply_markup=get_back_keyboard())
        return

    bot.send_message(chat_id, "❗ Некорректная команда 🙁", reply_markup=get_back_keyboard())

if __name__ == '__main__':
    init_db()
    print(f"Запуск бота с webhook: {WEBHOOK_URL}")
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
