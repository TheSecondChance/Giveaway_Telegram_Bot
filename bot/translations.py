from messages import *


am = {
    start_msg: """
እንኳን በደህና ወደ Giveaway መጡ!

የምዝገባ ሂድቱን ለማከናወን መመሪያ እና
እንዲሁም ጥያቄ ካሎት መልሶችን ያገኛሉ👍

""",
}

oro = {
    start_msg:""" Baga nagaan dhuftan  Giveaway Bot"""
}



translations = {
    "amharic": am,
    "oromic": oro,
}


def translate(text, lang):
    dict = translations.get(lang)
    if not dict:
        return text
    string = dict.get(text)

    if not string:
        return text
    return string
