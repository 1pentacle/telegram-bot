from flask import Flask, request
from telebot import TeleBot, types
import threading
import time

TOKEN = '7561769200:AAEbeAAAZLFAoO7WrnQgYpZ3jz3lOfHYRjQ'
bot = TeleBot(TOKEN)
app = Flask(__name__)

user_state = {}
registered_users = set()  # множество для подтверждённых user_id

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

@app.route('/postback', methods=['GET'])
def postback():
    # Принимаем параметры из GET-запроса
    args = request.args
    user_id = args.get('user_id') or args.get('affiliate_id')
    status = args.get('status')

    print(f"Postback received: user_id={user_id}, status={status}")

    if user_id and status == 'approved':
        registered_users.add(user_id)
        return 'OK', 200
    else:
        return 'Invalid data', 400

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
            if text in registered_users:
                bot.send_message(chat_id, f'✅ Ваш ID "{text}" подтверждён и вы зарегистрированы!', reply_markup=get_back_keyboard())
            else:
                bot.send_message(chat_id, '❗ Ошибка❗ Некорректный ввод ID или регистрация не подтверждена.', reply_markup=get_back_keyboard())
        else:
            bot.send_message(chat_id, '❗ Введите только цифры.', reply_markup=get_back_keyboard())
        return

    bot.send_message(chat_id, '❗ Некорректная команда 🙁', reply_markup=get_back_keyboard())

def run_flask():
    app.run(host="0.0.0.0", port=5000)

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Bot polling error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    # Запускаем Flask и бота параллельно
    threading.Thread(target=run_flask).start()
    run_bot()