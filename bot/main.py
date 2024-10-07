import os
import time
import telebot
from api import get_user, create_user, update_user
import threading
from telebot import types
from dotenv import load_dotenv
from messages import *
from translations import translate as _


load_dotenv()
INVITE_LINK = "https://t.me/GiveawayChallenge_bot?start={}"

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["language", ("language", "amharic")])
def select_language(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("English", callback_data="english")
    btn2 = types.InlineKeyboardButton("አማርኛ", callback_data="amharic")
    markup.add(btn1, btn2)
    with open('./Assets/languages.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="sdfslkdfj", reply_markup=markup)

def delete_message_after_delay(chat_id, message_id, delay_seconds):
    time.sleep(delay_seconds)
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

@bot.callback_query_handler(func=lambda call: call.data in ['english', 'amharic'])
def handle_language_selection(call: types.CallbackQuery):
    user = call.from_user
    response = get_user(telegram_id=user.id)
    if response != None:
        language = response.get('language')
    else:
        data = {
            "telegram_id": user.id,
            "is_taker": "false",
            "is_gifter": "false",
            "user_name": user.username,
            "language": call.data
        }
        create_user(created_data=data)
        response_user = get_user(telegram_id=user.id)
        language = response_user.get('language')

    msg = bot.send_message(call.message.chat.id, text=(
        f"Language Selected Successfully set {language}✅", language),)
    bot.delete_message(call.message.chat.id, call.message.id)

    bot.answer_callback_query(
        call.id,
        (f"The Language Preference is set to {language.capitalize()}", language),
    )

    response_user = get_user(telegram_id=user.id)
    msg.from_user = user
    is_not_phone_exisit = response_user.get('phone_number', None)

    if is_not_phone_exisit == None:
        request_contact_share(msg)
    else:
        welcome(msg)

def request_contact_share(message):
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    share = "📲 Share your contact to get started!"
    btn1 = types.KeyboardButton(("Share Contact 👩‍🎓"), request_contact=True)
    keyboard.add(btn1)

    with open('./Assets/share_contact.png', 'rb') as photo:
        response_message = bot.send_photo(
            message.chat.id, photo, caption=f"{share}",
            reply_markup=keyboard
        )
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed share to delete message {message.message_id}: {e}")

    threading.Thread(target=delete_message_after_delay, args=(message.chat.id, response_message.message_id, 10)).start()

@bot.message_handler(content_types=["contact"])
def handle_shared_contact(message: types.Message):
    try:
        contact = message.contact
        updated_data = {
            "phone_number": contact.phone_number,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "is_taker": False,
            "is_gifter": False,
            "is_active": True
        }
        update_user(telegram_id=contact.user_id, updated_data=updated_data)
    except Exception as e:
        print(f"Failed to save contact information to the database: {e}")
    response_message = bot.send_message(
        chat_id=message.chat.id,
        text=("Contact Received ✅")
    )
    threading.Thread(target=delete_message_after_delay, args=(message.chat.id, response_message.message_id, 1)).start()
    start(message)

@bot.message_handler(commands=['start', 'restart']) 
def start(message):
    user = get_user(telegram_id=message.from_user.id)
    if user != None:
        is_phone_exisit = user.get('phone_number')
        if is_phone_exisit is not None:
            welcome(message)
    else:
        select_language(message)
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"This is Failed start to delete message {message.message_id}: {e}")

@bot.message_handler(commands=['welcome']) 
def welcome(message, userId=None):
    user = get_user(telegram_id=message.from_user.id)
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    welcome_msg = _(start_msg, language)
    btn1 = types.InlineKeyboardButton(_("Giveter 🎁", language), callback_data="giveter")
    btn2 = types.InlineKeyboardButton(_("Taker 😉", language), callback_data="taker")
    btn3 = types.InlineKeyboardButton(_("Settings ⚙️", language), callback_data="settings")
    btn4 = types.InlineKeyboardButton(_("Invite Friends 🤝", language), url=INVITE_LINK)
    inline_markup.row(btn1, btn2)
    inline_markup.row(btn3, btn4)

    with open('./Assets/welcome_dr.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=welcome_msg, reply_markup=inline_markup)
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed welcome to delete message {message.message_id}: {e}")
   
@bot.callback_query_handler(func=lambda call: True)
def handle_call_back(callback):
    command = callback.data
    if command == "gifter":
        bot.delete_message(callback.message.chat.id, callback.message.id)
        bot.send_message(callback.message.chat.id, f'hellow {command.capitalize()}')
        bot.send_message(callback.message.chat.id, f'Your set to {command.capitalize()}')
    if command == "taker":
        """save gifter is_taker=True"""
        bot.delete_message(callback.message.chat.id, callback.message.id)
        bot.send_message(callback.message.chat.id, f'Your set to {command.capitalize()}')
    
bot.remove_webhook()
bot.infinity_polling()