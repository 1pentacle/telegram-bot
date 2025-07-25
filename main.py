from flask import Flask, request
from telebot import TeleBot, types
import os

TOKEN = '7561769200:AAEbeAAAZLFAoO7WrnQgYpZ3jz3lOfHYRjQ'
bot = TeleBot(TOKEN)
app = Flask(__name__)
user_state = {}

# Клавиатура "назад"
def get_back_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('↩️ Назад'))
    return keyboard

def step_start(message):
    user_state[message.chat.id] = 'start'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text='🖥️ Регистрация',
        url='https://pocketoption.com/ru/cabinet/registration?s=your_affiliate_link'
    ))
    markup.add(types.InlineKeyboardButton(
        text='✅ Я зарегистрировался',
        callback_data='registered'
    ))

    text = (
        'Привет! 👋\n\n'
        '📲 Чтобы получить доступ к приватному каналу, тебе необходимо стать моим партнёром...'
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
        if user_state.get(chat_id) == 'enter_id':
            step_start(message)
        else:
            bot.send_message(chat_id, "Вы уже на начальном шаге 👇", reply_markup=get_back_keyboard())
        return

    if user_state.get(chat_id) == 'enter_id':
        if text.isdigit():
            bot.send_message(chat_id, f'📩 Ваш ID "{text}" получен и отправлен на проверку!', reply_markup=get_back_keyboard())
        else:
            bot.send_message(chat_id, '❗ Введите только цифры.', reply_markup=get_back_keyboard())
        return

    bot.send_message(chat_id, '❗ Некорректная команда 🙁', reply_markup=get_back_keyboard())

# Обработка Webhook Telegram
@app.route(f"/bot{TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok', 200

@app.route('/')
def index():
    return 'Бот работает!', 200

# Установка Webhook при запуске
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/bot{TOKEN}")
    app.run(host="0.0.0.0", port=10000)