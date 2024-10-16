import telebot
from telebot import types
from messages import *
from translations import translate as _
from api import delete_account_api


def giver_settings(user, message, bot):
    first_name = user.get('first_name')
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    btn1 = types.InlineKeyboardButton(_("Change Language 🔊", language), callback_data="change_lang")
    btn2 = types.InlineKeyboardButton(_("Change Role ⚒️", language), callback_data="change_role")
    btn3 = types.InlineKeyboardButton(_("Back ⬅️", language), callback_data="home")
    btn4 = types.InlineKeyboardButton(_("Delete Account 🗑️", language), callback_data="delete_account")
    inline_markup.row(btn1, btn2)
    inline_markup.row(btn4, btn3)
    welcome_msg = f"Welcome {first_name} to this settings! \n\nHere you can change your language, role, and more."
    bot.send_message(message.chat.id, text=welcome_msg, reply_markup=inline_markup)

def change_language(message, bot):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("English", callback_data="english")
    btn2 = types.InlineKeyboardButton("አማርኛ", callback_data="amharic")
    markup.add(btn1, btn2)
    with open('./Assets/languages.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="Select you prefer language", reply_markup=markup)

def delete_account(user, message, bot):
    language = user.get('language', None)
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(_("Yes ✅", language), callback_data="delete_yes")
    btn2 = types.InlineKeyboardButton(_("No ❌", language), callback_data="home")
    inline_markup.add(btn1, btn2)
    bot.send_message(
        message.chat.id,
        text=_("Are you sure you want to delete your account?", language),
        reply_markup=inline_markup
        )

def delete_account_yes(user, message, bot, userId):
    language = user.get('language', None)
    delete_account_api(telegram_id=userId)
    bot.send_message(
        message.chat.id,
        text=_("Your account has been deleted successfully.", language)
        )
