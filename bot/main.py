import os
import io
import re
import time
import telebot
from .api import (get_user, create_user, update_user, create_question,
                 create_answer, giver_result, user_exists,
                 get_after_answer, update_after_answer)
import threading
from telebot import types
from dotenv import load_dotenv
from .messages import *
from .translations import translate as _
from .settings import (user_settings, change_language, delete_account, 
                       delete_account_yes, change_role)


load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
WELCOME_IMAGE = os.getenv('welcome_image')

def select_language(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("English", callback_data="english")
    btn2 = types.InlineKeyboardButton("አማርኛ", callback_data="amharic")
    markup.add(btn1, btn2)
    with open('./Assets/languages.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="Select your preferred language", reply_markup=markup)

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
        update_user(telegram_id=user.id, updated_data={"language": call.data, "first_name": user.first_name})
        language = response.get('language')
    else:
        data = {
            "first_name": user.first_name,
            "telegram_id": user.id,
            "user_name": user.username,
            "language": call.data
        }
        create_user(created_data=data)
        language = call.data

    msg = bot.send_message(call.message.chat.id, text=(
        f"Language Selected Successfully set {language}✅", language),)
    bot.delete_message(call.message.chat.id, call.message.id)

    bot.answer_callback_query(
        call.id,
        (f"The Language Preference is set to {language.capitalize()}", language),
    )
    msg.from_user = user
    start(msg)

@bot.message_handler(commands=['start', 'restart']) 
def start(message):
    user = get_user(telegram_id=message.chat.id)
    if user != None:
        language = user.get('language', None)
        is_telegram_id = user.get('telegram_id')
        is_giver = user.get('is_gifter')
        is_taker = user.get('is_taker')
        if is_giver == True:
            Giver_welcome(message, userId=message.chat.id)
        elif is_taker == True:
            taker_welcome(message, userId=message.chat.id) 
        elif is_telegram_id is not None:
            chose_role(language, message)
        else:
            select_language(message)
    else:
        select_language(message)
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"This is Failed start to delete message {message.message_id}: {e}")

def chose_role(language, message):
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    welcome_msg = _(choose_role, language)
    btn1 = types.InlineKeyboardButton(_("🎁 Give Reward", language), callback_data="giver")
    btn2 = types.InlineKeyboardButton(_("🧑‍💼 Get Reward", language), callback_data="taker")
    btn3 = types.InlineKeyboardButton(_("Back ⬅️", language), callback_data="home")
    inline_markup.row(btn1, btn2)
    inline_markup.row(btn3)

    bot.send_message(message.chat.id, text=welcome_msg, reply_markup=inline_markup)
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed chose to delete message {message.message_id}: {e}")

def Giver_welcome(message, userId=None):
    if userId:
        user = get_user(telegram_id=userId)
    else:
        user = get_user(telegram_id=message.chat.id)
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    msg = _(start_msg, language)
    btn1 = types.InlineKeyboardButton(_("Question Code 🧑‍💻", language), callback_data="question_code")
    btn2 = types.InlineKeyboardButton(_("Result 🧧", language), callback_data="result_giver")
    btn5 = types.InlineKeyboardButton(_("Insert Answer ✏️", language), callback_data="insert_answer")
    btn3 = types.InlineKeyboardButton(_("Settings ⚙️", language), callback_data="settings")
    btn4 = types.InlineKeyboardButton(_("Invite Friends 🤝", language), switch_inline_query="invite")
    inline_markup.row(btn1, btn2)
    inline_markup.row(btn5, btn3)
    inline_markup.row(btn4)

    with open('./Assets/welcome_dr.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=msg, reply_markup=inline_markup)
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
    msg = _(taker_msg, language)
    btn1 = types.InlineKeyboardButton(_("Answer 😎", language), callback_data="answer")
    btn2 = types.InlineKeyboardButton(_("Settings ⚙️", language), callback_data="settings")
    btn3 = types.InlineKeyboardButton(_("Invite Friends 🤝", language), switch_inline_query="invite")
    inline_markup.row(btn1, btn2)
    inline_markup.row(btn3)

    with open('./Assets/welcome_dr.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=msg, reply_markup=inline_markup)
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed welcome to delete message {message.message_id}: {e}")
    
@bot.callback_query_handler(func=lambda call: True)
def handle_call_back(callback):
    telegram_id=callback.message.chat.id
    user = get_user(telegram_id=telegram_id)

    if user is not None:
        command = callback.data
        language = user.get('language', None)
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
            msg = _(send_answer_msg, language)
            bot.send_message(callback.message.chat.id, msg)
            bot.register_next_step_handler(
                callback.message, handle_question_answer, telegram_id=telegram_id)

        if command == "home":
            start(callback.message)

        if command == "result_giver":
            telegram_id = callback.from_user.id
            msg = _(result_msg, language)
            bot.send_message(callback.message.chat.id, msg)
            bot.register_next_step_handler(
                callback.message, handle_giver_result, telegram_id=telegram_id)

        if command == "after":
            user = get_user(telegram_id=telegram_id)
            data = {}
            response = create_question(telegram_id=telegram_id, created_data=data)
            question_code = response.get('question_code')
            inline_markup = types.InlineKeyboardMarkup(row_width=2)
            copy_code = f"`{question_code}`"
            msg = _(after_code_msg, language)
            btn1 = types.InlineKeyboardButton(_("Back ⬅️", language), callback_data="home")
            inline_markup.row(btn1)

            bot.send_message(callback.message.chat.id, text=f"{msg}".format(copy_code),
                            reply_markup=inline_markup, parse_mode="Markdown")
            try:
                bot.delete_message(callback.message.chat.id, callback.message.message_id)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Failed welcome to delete message {callback.message.message_id}: {e}")

        if command == "answer":
            msg = _(answer_msg, language)
            bot.send_message(callback.message.chat.id, msg)
            bot.register_next_step_handler(
                callback.message, handle_taker_answer, telegram_id=telegram_id)

        if command == "settings":
            user_settings(user=user, message=callback.message, bot=bot)

        if command == "change_lang":
            change_language(language, callback.message, bot=bot)

        if command == "change_role":
            change_role(language ,callback.message, bot=bot)
 
        if command == "taker_home":
            taker_welcome(callback.message, userId=telegram_id)

        if command == "insert_answer":
            insert_answer(callback.message, userId=telegram_id)

        if command.isdigit():
            question_code = command
            user = get_user(telegram_id=telegram_id)

            bot.send_message(callback.message.chat.id,
                            f"you can now send your answer for 👉 {question_code}" )
            bot.register_next_step_handler(
                callback.message, update_question_answer, telegram_id=telegram_id,
                question_code=question_code)
            
        if command == "delete_account":
            delete_account(language, message=callback.message, bot=bot)

        if command == "delete_yes":
            delete_account_yes(user=user, message=callback.message, bot=bot, userId=telegram_id)
    else:
        start(callback.message)

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
    if response is not None:
        if response.get('status') == 201:
            welcome_msg = f"Answer Received ✅"
        elif response.get('status') == 404:
            welcome_msg = f"Answer not Received ❌ \n\n Resone: There is no question code"
        elif response.get('status') == 400:
            welcome_msg = f"Answer not Received ❌ \n\nPlease try again make sure you have entered the correct question code"
        else:
            welcome_msg = f"Answer not Received ❌ \n\nPlease try again something wrong in you answer format"
    else:
        welcome_msg = f"Answer not Received ❌ \n\nPlease try again make sure you have entered the correct question code"
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    btn1 = types.InlineKeyboardButton(_("Back ⬅️", language), callback_data="taker_home")
    inline_markup.row(btn1)
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
    btn2 = types.InlineKeyboardButton(_("Back ⬅️", language), callback_data="back")
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
        bot.send_document(telegram_id, document=pdf_file,
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

            btn1 = types.InlineKeyboardButton(_("Back ⬅️", language), callback_data="home")
            inline_markup.row(btn1)

            bot.send_message(telegram_id, text=f"Winers of question 👇 \n\n {question_code} 🥇🥇🥇",
                             reply_markup=inline_markup)
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed welcome to delete message {message.message_id}: {e}")

def question_answer_time(message, userId=None):
    user = get_user(telegram_id=userId)
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    question_code_msg = _(code_time_msg, language)
    btn1 = types.InlineKeyboardButton(_("📝 Now Answer", language), callback_data="now")
    btn2 = types.InlineKeyboardButton(_("📋 Later", language), callback_data="after")
    btn3 = types.InlineKeyboardButton(_("Back ⬅️", language), callback_data="home")
    inline_markup.row(btn1, btn2)
    inline_markup.row(btn3)
    bot.send_message(message.chat.id, text=question_code_msg, reply_markup=inline_markup)

    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed welcome to delete message {message.message_id}: {e}")

def back_buttons(user, message, welcome_msg):
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    btn1 = types.InlineKeyboardButton(_("Back ⬅️", language), callback_data="home")
    inline_markup.row(btn1)
    bot.send_message(message.chat.id, text=welcome_msg, reply_markup=inline_markup)

def insert_answer(message, userId=None):
    user = get_user(telegram_id=userId)
    language = user.get('language', None)
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    response = get_after_answer(telegram_id=userId)
    if response is not None:
        question_codes = [item['question_code'] for item in response['data']]
        for question_code in question_codes:
            msg = _(btn_insert_answer_mgs, language)
            button = types.InlineKeyboardButton(text=f"{msg}".format(question_code),
                                                callback_data=question_code)
            inline_markup.add(button)
        btn1 = types.InlineKeyboardButton(_("Back ⬅️", language), callback_data="home")
        inline_markup.row(btn1)
        msg = _(insert_answer_msg, language)
        bot.send_message(userId, text=msg, reply_markup=inline_markup)
    else:
        msg = _(insert_msg, language)
        back_buttons(user, message, msg)
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed welcome to delete message {message.message_id}: {e}")

def update_question_answer(message, telegram_id, question_code):
    user = get_user(telegram_id=telegram_id)
    answer = message.text
    telegram_id = message.chat.id
    data = {
        'correct_answer': answer,
    }
    update_after_answer(telegram_id=telegram_id, question_code=question_code, updated_data=data)
    question_code = question_code
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    welcome_msg = f"Answer Received ✅ for question {question_code}\n\n\n\n "
    btn1 = types.InlineKeyboardButton(_("Back ⬅️", language), callback_data="home")
    inline_markup.row(btn1)

    bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=welcome_msg, reply_markup=inline_markup, parse_mode="Markdown")
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed welcome to delete message {message.message_id}: {e}")

# bot.remove_webhook()
# bot.infinity_polling()