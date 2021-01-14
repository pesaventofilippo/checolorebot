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


def infoColore(colore: str):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="ℹ️ Cosa significa?", callback_data="infoColore#{}".format(colore))
    ]])


def categorieInfo(colore: str):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🍽 Attività Commerciali", callback_data="catInfo#{}#attcom".format(colore))
    ], [
        InlineKeyboardButton(text="🖥 Attività Professionali", callback_data="catInfo#{}#attpro".format(colore)),
    ], [
        InlineKeyboardButton(text="⚽️ Attività Sportive", callback_data="catInfo#{}#attsport".format(colore)),
    ], [
        InlineKeyboardButton(text="👥 Eventi / Riunioni", callback_data="catInfo#{}#eventi".format(colore)),
    ], [
        InlineKeyboardButton(text="🏢 Uffici Pubblici", callback_data="catInfo#{}#uffici".format(colore)),
    ], [
        InlineKeyboardButton(text="📄 Sanzioni", callback_data="catInfo#{}#sanzioni".format(colore)),
        InlineKeyboardButton(text="🚗 Spostamenti", callback_data="catInfo#{}#sposta".format(colore)),
    ], [
        InlineKeyboardButton(text="🎓 Università", callback_data="catInfo#{}#uni".format(colore)),
        InlineKeyboardButton(text="👷 Lavoro", callback_data="catInfo#{}#lavoro".format(colore)),
    ], [
        InlineKeyboardButton(text="😷 Mascherine", callback_data="catInfo#{}#mascherine".format(colore)),
    ]])


def backInfo(colore: str):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="◀️ Indietro", callback_data="infoColore#{}".format(colore))
    ]])
