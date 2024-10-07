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
            "user_name": user.username,
            "language": call.data
        }
        create_user(created_data=data)
        response_user = get_user(telegram_id=user.id)
        language = call.data

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
        start(msg)

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
    threading.Thread(target=delete_message_after_delay, args=(
        message.chat.id, response_message.message_id, 1)).start()
    
    start(message)

@bot.message_handler(commands=['start', 'restart']) 
def start(message):
    user = get_user(telegram_id=message.from_user.id)
    if user != None:
        is_phone_exisit = user.get('phone_number')
        is_giver = user.get('is_gifter')
        is_taker = user.get('is_taker')
        if is_giver == True:
            Giver_welcome(message)
        elif is_taker == True:
            taker_welcome(message) 
        elif is_phone_exisit is not None:
            chose_role(message)
        else:
            select_language(message)
    else:
        select_language(message)
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"This is Failed start to delete message {message.message_id}: {e}")

def chose_role(message):

    user = get_user(telegram_id=message.from_user.id)
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    welcome_msg = _(choose_role, language)
    btn1 = types.InlineKeyboardButton(_("Giver 🎁", language), callback_data="giver")
    btn2 = types.InlineKeyboardButton(_("Taker 😉", language), callback_data="taker")
    inline_markup.row(btn1, btn2)

    with open('./Assets/languages.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=welcome_msg, reply_markup=inline_markup)
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed chose to delete message {message.message_id}: {e}")

def Giver_welcome(message, userId=None):
    if userId:
        user = get_user(telegram_id=userId)
    else:
        user = get_user(telegram_id=message.from_user.id)
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    welcome_msg = _(start_msg, language)
    btn1 = types.InlineKeyboardButton(_("Question Code 🧑‍💻", language), callback_data="question_code")
    btn2 = types.InlineKeyboardButton(_("Result 🧧", language), callback_data="taker")
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

def taker_welcome(message, userId=None):
    if userId:
        user = get_user(telegram_id=userId)
    else:
        user = get_user(telegram_id=message.from_user.id)
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    welcome_msg = _(start_msg, language)
    btn1 = types.InlineKeyboardButton(_("Answer ⭐", language), callback_data="answer")
    btn2 = types.InlineKeyboardButton(_("Settings ⚙️", language), callback_data="settings")
    btn3 = types.InlineKeyboardButton(_("Invite Friends 🤝", language), url=INVITE_LINK)
    inline_markup.row(btn1, btn2)
    inline_markup.row(btn3)

    with open('./Assets/welcome_dr.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=welcome_msg, reply_markup=inline_markup)
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed welcome to delete message {message.message_id}: {e}")
   
@bot.callback_query_handler(func=lambda call: True)
def handle_call_back(callback):
    command = callback.data
    telegram_id=callback.message.chat.id

    if command == "giver":
        data = {
            "is_gifter": True,
            "is_taker": False,
        }

        update_user(telegram_id=telegram_id, updated_data=data)
        Giver_welcome(callback.message, userId=telegram_id)

    if command == "taker":
        data = {
            "is_gifter": False,
            "is_taker": True,
        }
        update_user(telegram_id=telegram_id, updated_data=data)
        taker_welcome(callback.message, userId=telegram_id)
    
bot.remove_webhook()
bot.infinity_polling()