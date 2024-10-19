from .messages import *


am = {
    start_msg: """
🎉 ወደ ስጦታ ቦት እንኳን በደህና መጡ! 🎉


🔢 የጥያቄ ኮድ - ለጥያቄዎችዎ ኮድ ይፍጠሩ

🧧 ውጤት - በተቀባዮች የቀረቡ ትክክለኛ መልሶችን ይመልከቱ

✏️ መልስ አስገባ - መልስ የሌለው ጥያቄ ካለ መልስ ያስገቡ

⚙️ መቼቶች - ቋንቋ እና ሚና ለመቀየር ፣ መለያዎን ይሰርዙ
""",

"Question Code 🧑‍💻": "የጥያቄ ኮድ 🧑‍💻",
"Result 🧧": "ውጤት 🧧",
"Insert Answer ✏️": "መልስ አስገባ ✏️",
"Settings ⚙️": "መቼቶች ⚙️",
"Invite Friends 🤝": "ጓደኛዎን ይጋብዙ 🤝",

choose_role: """🤔 ሚናህን ምረጥ


🎁 ሽልማት ይስጡ - ለትክክለኛ መልስ ሽልማትን ይስጡ።

🧑‍💼 ሽልማት ያግኙ - ጥያቄውን ይመልሱ እና ሽልማትዎን ያግኙ!"
""",

change_role_mgs: """🤔 ሚናህን ቀይር

⚠️ ማሳሰቢያ፡ ሚናህን መቀየር የቀደመ ፋይሎችን ያጠፋል


🎁 ሽልማት ይስጡ - ለትክክለኛ መልስ ሽልማትን ይስጡ።

🧑‍💼 ሽልማት ያግኙ - ጥያቄውን ይመልሱ እና ሽልማትዎን ያግኙ!"
""",

"🎁 Give Reward": "🎁 ሽልማት ይስጡ",
"🧑‍💼 Get Reward": "🧑‍💼 ሽልማት ያግኙ",


code_time_msg: """
🔢  የምትፈልገውን የጥያቄ ኮድ አይነት ንካ።


📝 አሁን መልስ - መልስዎን ያስገቡ እና ኮድ ይፍጠሩ

📋 በኋላ - የጥያቄ ኮድ ብቻ ይፍጠሩ
""",

"📝 Now Answer": "📝 አሁን መልስ",
"📋 Later": "📋 በኋላ",

send_answer_msg: """
አሁን መልስዎን መላክ ይችላሉ! 📩 

መልስዎን ካስገቡ በኋላ የጥያቄ ኮድ ያገኛሉ
""",

after_code_msg: """
እባክህ ይህን ኮድ በጥያቄህ ዝርዝር ውስጥ አስገባ 📋፡ \n\n 👉  {0}
""", 

result_msg: """ውጤቱን ለማግኘት የጥያቄ ኮድ ይላኩ! 📩 """,

insert_answer_msg: "መልስዎን ለማስገባት የጥያቄ ኮድ ይምረጡ 📝",

btn_insert_answer_mgs: "ኮድ 👉 {0} ",

"Back ⬅️": "ተመለስ ⬅️",

setting_msg: """
⚙️ {0} እነዚህ የእርስዎ ቅንብሮች ናቸው!


🌐 ቋንቋ ቀይር፡ የመረጥከውን ቋንቋ ቀይር

🔄 ሚናን ቀይር፡ ሰጪ ወይም ተቀባይ መቀያየር

🗑️ መለያ ሰርዝ፡ መለያህን እስከመጨረሻው አስወግድ
""",

"🌐 Change Language": "🌐 ቋንቋ ቀይር",
"🔄 Change Role": "🔄 ሚናን ቀይር",
"🗑️ Delete Account": "🗑️ መለያ ሰርዝ",

select_lang_mgs: "🌍 ቋንቋ ይምረጡ",

delete_account_msg: "እርግጠኛ ነህ መለያህን መሰረዝ ትፈልጋለህ? 🤔",

"Yes ✅": "አዎ ✅",
"No ❌": "አይ ❌",

insert_msg: "ጥያቄህ ሁሉ ትክክለኛ መልስ አለው 😊",

delete_mgs: "የእርስዎ መለያ በተሳካ ሁኔታ ተሰርዟል! 🚮",

taker_msg: """
🎉 ወደ ስጦታ ቦት እንኳን በደህና መጡ! 🎉


🔢 መልስ - ጥያቄን ለመመለስ እባክዎን ከመልሶዎ በፊት የጥያቄ ኮድ ያስገቡ

⚙️ መቼቶች - ቋንቋ እና ሚና ለመቀየር ፣ መለያዎን ይሰርዙ
""",

"Answer 😎": "መልስ",

answer_msg: "አሁን መልስህን መላክ ትችላለህ 📩"

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
