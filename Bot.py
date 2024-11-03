import telebot
from telebot import types
import json

# Токен вашего бота
TOKEN = ''
# Ваш Telegram ID
ADMIN_TELEGRAM_ID = '5614647931'
# Файлы для хранения данных
USER_IDS_FILE = 'user_ids.json'
USER_INFO_FILE = 'user_info.txt'

# Создание объекта бота
bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()

# Функция для загрузки ID пользователей из файла
def load_user_ids():
    try:
        with open('user_ids.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.decoder.JSONDecodeError:
        return []


# Функция для сохранения ID пользователей в файл
def save_user_ids(user_ids):
    with open(USER_IDS_FILE, 'w') as file:
        json.dump(user_ids, file)


# Функция для записи информации о пользователях в файл
def save_user_info(user_id, username):
    with open(USER_INFO_FILE, 'a') as file:
        file.write(f"{user_id} {username}\n")


# Загрузка ID пользователей
user_ids = load_user_ids()


# Обработчик для кнопки "/start"
@bot.message_handler(commands=['start'])
def handle_start(message):
    hello = ("Добро пожаловать! Напишите ID пользователя кому бы вы хотели отправить анонимное сообщение. Узнать ID [тут](https://t.me/getmy_idbot/)",
             'Лучший ванильный ReDrak(@ReDarkserv)')
    bot.send_message(message.chat.id, hello, parse_mode='Markdown')
    bot.register_next_step_handler(message, handle_message)

    # Сохраняем ID и имя пользователя
    if message.chat.id not in user_ids:
        user_ids.append(message.chat.id)
        save_user_ids(user_ids)
        save_user_info(message.chat.id, message.chat.username)

def handle_message(message): 
    TO_USER_MESSAGE = message.text 
    bot.send_message(message.chat.id, "Напишите сообщение:") 
    bot.register_next_step_handler(message, receive_question, TO_USER_MESSAGE) 
    

# Обработчик получения вопроса от пользователя
def receive_question(message, TO_USER_MESSAGE):
    user_question = message.text
    if user_question:
        bot.send_message(message.chat.id, "Сообщение доставлено")
        bot.send_message(TO_USER_MESSAGE, f"Получено новое анонимное сообщение: {user_question}")
    else:
        bot.send_message(message.chat.id, "Вопрос не получен. Пожалуйста, попробуйте еще раз.")

# Обработчик для кнопки "Test"
@bot.message_handler(func=lambda message: message.text == 'Panel' and message.chat.username == 'Nik_610')
def handle_test(message):
    markup = types.InlineKeyboardMarkup()
    btn_off = types.InlineKeyboardButton(text="Выключить бота", callback_data="turn_off")
    btn_on = types.InlineKeyboardButton(text="Включить бота", callback_data="turn_on")
    btn_post = types.InlineKeyboardButton(text="Сделать пост", callback_data="send_post")
    markup.add(btn_off, btn_on, btn_post)

    bot.send_message(message.chat.id, 'Admin panel', reply_markup=markup)


# Обработчик для других пользователей, если они отправляют "Test"
@bot.message_handler(func=lambda message: message.text == 'Panel' and message.chat.username != 'Nik_610')
def handle_test_other_users(message):
    bot.send_message(message.chat.id, "У вас нет доступа к этой команде.")


# Обработчики для инлайн-кнопок
@bot.callback_query_handler(func=lambda call: call.data == 'turn_off')
def handle_turn_off(call):
    bot.send_message(call.message.chat.id, "Бот выключен.")

@bot.callback_query_handler(func=lambda call: call.data == 'turn_on')
def handle_turn_on(call):
    bot.send_message(call.message.chat.id, "Бот включен.")

@bot.callback_query_handler(func=lambda call: call.data == 'send_post')
def handle_send_post_init(call):
    bot.send_message(call.message.chat.id, "Напишите содержание поста для всех пользователей:")
    bot.register_next_step_handler(call.message, get_post_content)


# Обработчик для получения текста поста
def get_post_content(message):
    post_message = message.text
    if post_message:
        bot.send_message(message.chat.id, "Сообщение было разослано всем пользователям.")
        send_post_to_all_users(post_message)
    else:
        bot.send_message(message.chat.id, "Сообщение не может быть пустым.")


# Функция для отправки поста всем пользователям
def send_post_to_all_users(post_message):
    for user_id in user_ids:
        try:
            bot.send_message(user_id, post_message)
        except Exception as e:
            print(f"Failed to send message to user {user_id}: {e}")

# Запуск бота
while True:
    bot.polling()
