import os
from flask import Flask, request
from telebot import TeleBot, types

TOKEN = os.getenv('TOKEN')  # В Render нужно указать переменную окружения TOKEN
WEBHOOK_URL = f"https://telegram-bot-l2vg.onrender.com/{TOKEN}"  # Укажи свой Render-домен

bot = TeleBot(TOKEN)
app = Flask(__name__)
user_state = {}  # Храним состояние пользователя (в памяти)

# 📍 Кнопка "Регистрация", "Я зарегистрировался" и новая "Что такое OptiX?"
def get_start_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text='🖥️ Регистрация',
        url='https://u3.shortink.io/register?utm_campaign=823619&utm_source=affiliate&utm_medium=sr&a=gmURbwjR6oRBDh&ac=ttrade404&code=DEV906'  # Замени ссылку!
    ))
    markup.add(types.InlineKeyboardButton(
        text='✅ Я зарегистрировался',
        callback_data='registered'
    ))
    markup.add(types.InlineKeyboardButton(
        text='🤖 Что такое OptiX?',
        callback_data='optix_info'
    ))
    return markup

# 📍 Кнопка "Назад"
def get_back_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton('↩️ Назад'))
    return keyboard

# 📍 Сообщение при старте
def send_start_message(chat_id):
    user_state[chat_id] = 'start'
    text = (
        "👋 Привет! Добро пожаловать в *OptiX* — твой путь к реальному доходу на трейдинге 💸\n\n"
        "Здесь нет воды и бесполезных прогнозов — только рабочие стратегии, чёткие сигналы и результат. "
        "Ты получишь доступ в приватный канал, где каждый день мы зарабатываем вместе 📊\n\n"
        "*Чтобы начать:*\n\n"
        "✅ *Шаг 1:* Зарегистрируйся на Pocket Option по кнопке ниже\n"
        "📌 *Важно:*\n"
        "— Аккаунт должен быть *новым*\n"
        "— Введи промокод *DEV906* — получишь *+60% бонус* к пополнению!\n\n"
        "✅ *Шаг 2:* Нажми кнопку *«Я зарегистрировался»* и пришли свой *ID аккаунта*\n\n"
        "После этого ты получишь ссылку на приват, где уже зарабатывают десятки трейдеров каждый день 🔥\n\n"
        "🎯 Если ты действительно хочешь вырваться из круга \"проб и ошибок\" и начать получать стабильную прибыль — ты по адресу. Не упусти шанс.\n\n"
        "👇 *Действуй прямо сейчас и начни с преимуществом:*"
    )
    bot.send_message(chat_id, text, reply_markup=get_start_keyboard(), parse_mode='Markdown')

# 📍 Сообщение "Введите ID"
def send_enter_id_message(chat_id):
    user_state[chat_id] = 'enter_id'
    bot.send_message(chat_id, "✅ Введите свой ID (цифры):", reply_markup=get_back_keyboard())

# 📍 Проверка ID из файла verified_ids.txt
def check_pocket_option_id(user_id):
    try:
        with open("verified_ids.txt", "r") as file:
            ids = file.read().splitlines()
        return user_id in ids
    except FileNotFoundError:
        return False

# 📍 POST-запрос от Telegram (webhook)
@app.route(f"/{TOKEN}", methods=['POST'])
def telegram_webhook():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

# 📍 POSTBACK от Pocket Option
@app.route("/postback", methods=["GET", "POST"])
def postback():
    data = request.args or request.form
    trader_id = data.get("trader_id")
    event = data.get("reg") or data.get("ftd") or data.get("dep")

    if trader_id and event:
        with open("verified_ids.txt", "a") as file:
            file.write(trader_id + "\n")
        return "OK", 200
    return "Missing data", 400

# 📍 Команда /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    send_start_message(message.chat.id)

# 📍 Обработка нажатия на "Я зарегистрировался"
@bot.callback_query_handler(func=lambda call: call.data == 'registered')
def handle_registered(call):
    bot.answer_callback_query(call.id)
    send_enter_id_message(call.message.chat.id)

# 📍 Обработка нажатия на кнопку "Что такое OptiX?"
@bot.callback_query_handler(func=lambda call: call.data == 'optix_info')
def handle_optix_info(call):
    bot.answer_callback_query(call.id)
    text = (
        "💼 OptiX — трейдинг нового поколения\n\n"
        "Забудь про “гуру” и сигналы от людей, которые сами не уверены в своих входах.\n"
        "В OptiX мы пошли дальше — мы создали AI, который анализирует рынок и даёт сигналы с высокой точностью, 24/7.\n\n"
        "🔹 OptiX — это закрытое трейдинг-сообщество, где нет места хаосу, эмоциям и \"методам интуиции\".\n"
        "🔹 Это платформа, построенная на искусственном интеллекте, который сам находит лучшие точки входа на бинарных опционах.\n\n"
        "🚀 Что ты получаешь:\n\n"
        "✔ AI-бот, дающий чёткие сигналы по отработанным алгоритмам\n"
        "✔ Закрытый канал с доступом к этим сигналам 24/7\n"
        "✔ Пошаговые гайды, как торговать даже без опыта\n"
        "✔ Моментальный старт — зарегистрировался и сразу получил доступ\n"
        "✔ Всё полностью автоматизировано — ты просто следуешь сигналам\n\n"
        "❗ Мы не обучаем. Мы не ведём за руку.\n"
        "Мы дали тебе инструмент, который работает. И ты либо используешь его, либо упускаешь шанс.\n\n"
        "💡 OptiX — когда технология работает за тебя.\n"
        "Добро пожаловать в будущее трейдинга."
    )
    bot.send_message(call.message.chat.id, text)

# 📍 Обработка всех сообщений
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
                bot.send_message(chat_id, f"✅ Ваш ID {text} подтверждён! Спасибо 🙌", reply_markup=types.ReplyKeyboardRemove())
                user_state[chat_id] = 'verified'
                # Здесь можно добавить ссылку на канал или следующий шаг
            else:
                bot.send_message(chat_id, "❗ Ваш ID не найден. Убедитесь, что вы зарегистрировались по моей ссылке и подождите пару минут.", reply_markup=get_back_keyboard())
        else:
            bot.send_message(chat_id, "❗ Пожалуйста, введите только цифры.", reply_markup=get_back_keyboard())
        return

    bot.send_message(chat_id, "❗ Я не понял команду. Нажми 'Назад'.", reply_markup=get_back_keyboard())

# 📍 Запуск приложения
if __name__ == '__main__':
    print(f"Запуск бота с webhook: {WEBHOOK_URL}")
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))