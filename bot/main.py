import os
import io
import re
import time
import telebot
from api import (get_user, create_user, update_user, create_question,
                 create_answer, giver_result, user_exists)
import threading
from telebot import types
from dotenv import load_dotenv
from messages import *
from translations import translate as _


load_dotenv()
INVITE_LINK = "https://t.me/GiveawayChallenge_bot?start={}"

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
WELCOME_IMAGE = os.getenv('welcome_image')

# @bot.message_handler(commands=["language", ("language", "amharic")])
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
    user = get_user(telegram_id=message.chat.id)
    if user != None:
        is_phone_exisit = user.get('phone_number')
        is_giver = user.get('is_gifter')
        is_taker = user.get('is_taker')
        if is_giver == True:
            Giver_welcome(message, userId=message.chat.id)
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
    btn2 = types.InlineKeyboardButton(_("Result 🧧", language), callback_data="result_giver")
    btn3 = types.InlineKeyboardButton(_("Settings ⚙️", language), callback_data="settings")
    btn4 = types.InlineKeyboardButton(_("Invite Friends 🤝", language), url=INVITE_LINK)
    inline_markup.row(btn1, btn2)
    inline_markup.row(btn3, btn4)

    bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=welcome_msg, reply_markup=inline_markup)

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

    if command == "question_code":
        question_answer_time(callback.message, userId=telegram_id)

    if command == "now":
        telegram_id = callback.from_user.id
        bot.send_message(callback.message.chat.id,
                         "you can now send your answer" )
        bot.register_next_step_handler(
            callback.message, handle_question_answer, telegram_id=telegram_id)
        
    if command == "home":
        start(callback.message)
        
    if command == "result_giver":
        telegram_id = callback.from_user.id
        bot.send_message(callback.message.chat.id,
                         "you can now send question code" )
        bot.register_next_step_handler(
            callback.message, handle_giver_result, telegram_id=telegram_id)
        
    if command == "after":
        user = get_user(telegram_id=telegram_id)
        data = {}
        response = create_question(telegram_id=telegram_id, created_data=data)
        question_code = response.get('question_code')
        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        language = user.get('language', None)
        copy_code = f"`{question_code}`"
        welcome_msg = f"Please past this code on you question details 👇\n\n {copy_code}"
        btn1 = types.InlineKeyboardButton(_("Home 🏠", language), callback_data="home")
        btn2 = types.InlineKeyboardButton(_("Back 🔙", language), callback_data="back")
        inline_markup.row(btn1, btn2)

        bot.send_message(callback.message.chat.id, text=welcome_msg, reply_markup=inline_markup, parse_mode="Markdown")
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Failed welcome to delete message {callback.message.message_id}: {e}")
    if command == "answer":
        telegram_id = callback.from_user.id
        bot.send_message(callback.message.chat.id,
                         "you can now send your answer" )
        bot.register_next_step_handler(
            callback.message, handle_taker_answer, telegram_id=telegram_id)

def handle_taker_answer(message, telegram_id):
    user = get_user(telegram_id=telegram_id)
    telegram_id = message.from_user.id
    message_text = message.text.strip()
    match = re.match(r"(\d+)\s+(.*)", message_text)

    if match:
        question_code = match.group(1)
        answer = match.group(2)
    else:
        question_code = None
        answer = message_text
    data = {
        'answer_text': answer,
        'question_code': question_code
    }
    response = create_answer(telegram_id=telegram_id, created_data=data)
    if response.get('status') == 201:
        welcome_msg = f"Answer Received ✅"
    elif response.get('status') == 404:
        welcome_msg = f"Answer not Received ❌ \n\n Resone: There is no question code"
    else:
        welcome_msg = f"Answer not Received ❌ \n\n Resone: you can answer only once"
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    btn1 = types.InlineKeyboardButton(_("Home 🏠", language), callback_data="taker_home")
    btn2 = types.InlineKeyboardButton(_("Back 🔙", language), callback_data="back")
    inline_markup.row(btn1, btn2)
    bot.send_message(message.chat.id, text=welcome_msg, reply_markup=inline_markup)

def handle_question_answer(message, telegram_id):
    user = get_user(telegram_id=telegram_id)
    answer = message.text
    telegram_id = message.from_user.id
    data = {
        'correct_answer': answer,
    }
    response = create_question(telegram_id=telegram_id, created_data=data)
    question_code = response.get('question_code')
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    copy_code = f"`{question_code}`"
    welcome_msg = f"Answer Received ✅ \n\nPlease past this code on you question details 👇\n\n {copy_code} "
    btn1 = types.InlineKeyboardButton(_("Home 🏠", language), callback_data="home")
    btn2 = types.InlineKeyboardButton(_("Back 🔙", language), callback_data="back")
    inline_markup.row(btn1, btn2)

    bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=welcome_msg, reply_markup=inline_markup, parse_mode="Markdown")
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed welcome to delete message {message.message_id}: {e}")

def handle_giver_result(message, telegram_id):
    user = get_user(telegram_id=telegram_id)
    question_code = message.text
    telegram_id = message.from_user.id
    language = user.get('language', None)
    if question_code.isdigit() == False:
        welcome_msg = "Please enter question code to get result"
        bot.send_message(message.chat.id, text=welcome_msg)
        return
    response = giver_result(telegram_id=telegram_id, question_code=question_code)
    if response.headers.get('Content-Type') == 'application/pdf':
        pdf_file = io.BytesIO(response.content)
        pdf_file.seek(0) 
        bot.send_document(chat_id=6296919002, document=pdf_file,
        visible_file_name='correct_answers.pdf',
        caption=f"Here are the correct answers for question {question_code} in PDF format."
        )
    else:
        response = response.json()
        if response.get('status') == 404:
            welcome_msg = "No question found with the provided question_code"
            back_buttons(user, message, welcome_msg)
            return
        correct_answers = response.get('correct_answers', [])
        if not correct_answers:
            welcome_msg = "There is no correct answer 😢 \n\n"
        else:
            inline_markup = types.InlineKeyboardMarkup(row_width=2)
            valid_users = []
            for answer in correct_answers:
                taker_id = answer.get('taker_id')
                bot_send=bot
                if user_exists(taker_id, bot_send):
                    valid_users.append(taker_id)
            for valid_user in valid_users:
                button = types.InlineKeyboardButton(text="Click to send a givet 💬", url=f"tg://user?id={valid_user}")
                inline_markup.add(button)

            btn1 = types.InlineKeyboardButton(_("Home 🏠", language), callback_data="home")
            btn2 = types.InlineKeyboardButton(_("Back 🔙", language), callback_data="back")
            inline_markup.row(btn1, btn2)

            bot.send_message(chat_id=6296919002, text=f"Winers of question 👇 \n\n {question_code} 🥇🥇🥇",
                             reply_markup=inline_markup)
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed welcome to delete message {message.message_id}: {e}")

def question_answer_time(message, userId=None):
    user = get_user(telegram_id=userId)
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    welcome_msg = _(start_msg, language)
    btn1 = types.InlineKeyboardButton(_("I know answer now 🚀", language), callback_data="now")
    btn2 = types.InlineKeyboardButton(_("After taker submite 😉", language), callback_data="after")
    btn3 = types.InlineKeyboardButton(_("Back 🔙", language), callback_data="home")
    inline_markup.row(btn1, btn2)
    inline_markup.row(btn3)
    bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=welcome_msg, reply_markup=inline_markup)

    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed welcome to delete message {message.message_id}: {e}")

def back_buttons(user, message, welcome_msg):
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    btn1 = types.InlineKeyboardButton(_("Home 🏠", language), callback_data="home")
    btn2 = types.InlineKeyboardButton(_("Back 🔙", language), callback_data="home")
    inline_markup.row(btn1, btn2)
    bot.send_message(message.chat.id, text=welcome_msg, reply_markup=inline_markup)

bot.remove_webhook()
bot.infinity_polling()