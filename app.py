import telebot
from telebot import types

API_TOKEN = '7305892783:AAEPYSCoF2PQuUxdTToS1zlEYvR9yZv4gjs'
bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения информации о постах пользователей
user_posts = {}

# Проверка на администратора
def is_admin(chat_id, user_id):
    chat_administrators = bot.get_chat_administrators(chat_id)
    for admin in chat_administrators:
        if admin.user.id == user_id:
            return True
    return False

# Функция для создания поста
def create_post(user_id, message):
    if user_id not in user_posts:
        user_posts[user_id] = []

    user_posts[user_id].append(message)

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я помогу тебе создать и разослать посты. Отправь сообщение, чтобы начать.")

# Обработка сообщений с медиафайлами и текстом
@bot.message_handler(content_types=['text', 'photo', 'video', 'audio', 'voice', 'document', 'sticker'])
def handle_message(message):
    user_id = message.from_user.id

    # Сохраняем пост пользователя
    create_post(user_id, message)

    # Создаем инлайн-кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    select_groups_button = types.InlineKeyboardButton(text="Выбрать группы для рассылки", callback_data="select_groups")
    markup.add(select_groups_button)

    bot.send_message(user_id, "Сообщение сохранено. Что будем делать дальше?", reply_markup=markup)

# Обработка нажатий на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id

    if call.data == "select_groups":
        # Получаем список групп, где бот является администратором
        groups = []  # Здесь можно подставить реальные ID групп или чатов, где бот админ

        # Создаем кнопки для выбора групп
        markup = types.InlineKeyboardMarkup()
        for group in groups:
            markup.add(types.InlineKeyboardButton(text=f"Группа {group}", callback_data=f"send_to_group_{group}"))

        bot.send_message(user_id, "Выберите группы для рассылки:", reply_markup=markup)

    elif call.data.startswith("send_to_group_"):
        group_id = call.data.split("_")[-1]

        # Отправляем сохраненный пост в выбранную группу
        if user_id in user_posts:
            for post in user_posts[user_id]:
                try:
                    # Определяем тип контента и отправляем соответствующее сообщение
                    if post.content_type == 'text':
                        bot.send_message(group_id, post.text)
                    elif post.content_type == 'photo':
                        bot.send_photo(group_id, post.photo[-1].file_id, caption=post.caption)
                    elif post.content_type == 'video':
                        bot.send_video(group_id, post.video.file_id, caption=post.caption)
                    elif post.content_type == 'audio':
                        bot.send_audio(group_id, post.audio.file_id, caption=post.caption)
                    elif post.content_type == 'voice':
                        bot.send_voice(group_id, post.voice.file_id)
                    elif post.content_type == 'document':
                        bot.send_document(group_id, post.document.file_id, caption=post.caption)
                    elif post.content_type == 'sticker':
                        bot.send_sticker(group_id, post.sticker.file_id)
                except Exception as e:
                    bot.send_message(user_id, f"Ошибка при отправке в группу {group_id}: {e}")

            bot.send_message(user_id, f"Посты успешно отправлены в группу {group_id}!")
        else:
            bot.send_message(user_id, "У вас нет сохраненных постов.")

bot.polling()