import telebot
from telebot import types
from .messages import *
from .translations import translate as _
from .api import delete_account_api


def user_settings(user, message, bot):
    first_name = user.get('first_name')
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    language = user.get('language', None)
    msg = _(setting_msg, language)
    btn1 = types.InlineKeyboardButton(_("🌐 Change Language", language), callback_data="change_lang")
    btn2 = types.InlineKeyboardButton(_("🔄 Change Role", language), callback_data="change_role")
    btn3 = types.InlineKeyboardButton(_("Back ⬅️", language), callback_data="home")
    btn4 = types.InlineKeyboardButton(_("🗑️ Delete Account", language), callback_data="delete_account")
    btn5 = types.InlineKeyboardButton(_("💬 Send Comments", language), callback_data="send_comments")
    inline_markup.row(btn1, btn2)
    inline_markup.row(btn4, btn5)
    inline_markup.row(btn3)
    bot.send_message(message.chat.id, text=f"{msg}".format(first_name), reply_markup=inline_markup)

def change_language(language, message, bot):
    msg = _(select_lang_mgs, language)
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("English", callback_data="english")
    btn2 = types.InlineKeyboardButton("አማርኛ", callback_data="amharic")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text=msg, reply_markup=markup)
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed chose to delete message {message.message_id}: {e}")

def delete_account(language, message, bot):
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(_("Yes ✅", language), callback_data="delete_yes")
    btn2 = types.InlineKeyboardButton(_("No ❌", language), callback_data="home")
    inline_markup.add(btn1, btn2)
    msg = _(delete_account_msg, language)
    bot.send_message(
        message.chat.id, text=msg, reply_markup=inline_markup)
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed chose to delete message {message.message_id}: {e}")

def delete_account_yes(user, message, bot, userId):
    language = user.get('language', None)
    delete_account_api(telegram_id=userId)
    msg = _(delete_mgs, language)
    send_msg = bot.send_message(message.chat.id, text=msg)
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed chose to delete message {message.message_id}: {e}")
    return send_msg.message_id


def change_role(language, message, bot):
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    msg = _(change_role_mgs, language)
    btn1 = types.InlineKeyboardButton(_("🎁 Give Reward", language), callback_data="giver")
    btn2 = types.InlineKeyboardButton(_("🧑‍💼 Get Reward", language), callback_data="taker")
    btn3 = types.InlineKeyboardButton(_("Back ⬅️", language), callback_data="home")
    inline_markup.row(btn1, btn2)
    inline_markup.row(btn3)

    bot.send_message(message.chat.id, text=msg, reply_markup=inline_markup)
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed chose to delete message {message.message_id}: {e}")