from telepotpro.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from modules.helpers import regionList


def regions():
    keyboard = []
    line = []
    for name in regionList:
        line.append(InlineKeyboardButton(text=name, callback_data="setregion#{}".format(name)))
        if len(line) == 2:
            keyboard.append(line.copy())
            line.clear()
    if len(line) > 0:
        keyboard.append(line.copy())
        line.clear()
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
