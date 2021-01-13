from telepotpro.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from modules.helpers import regionList


def regions():
    keyboard = []
    for n in range(0, 20, 2):
        first = regionList[n]
        second = regionList[n+1]
        keyboard.append([
            InlineKeyboardButton(text=first, callback_data="setregion#{}".format(first)),
            InlineKeyboardButton(text=second, callback_data="setregion#{}".format(second)),
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def orari():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🕙 -30 min.", callback_data="notifTime#minus"),
        InlineKeyboardButton(text="🕙 +30 min.", callback_data="notifTime#plus")
    ], [
        InlineKeyboardButton(text="✅ Fatto", callback_data="notifTime#done")
    ]])


def notifiche():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔔 Attiva", callback_data="notifToggle#on"),
        InlineKeyboardButton(text="🔕 Disattiva", callback_data="notifToggle#off")
    ], [
        InlineKeyboardButton(text="✅ Fatto", callback_data="notifToggle#done")
    ]])
