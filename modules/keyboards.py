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


def categorieInfo(colore: str, page: int=0):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🍽 Attività Commerciali", callback_data="catInfo#{}#attcom#{}".format(colore, page))
    ], [
        InlineKeyboardButton(text="🖥 Attività Professionali", callback_data="catInfo#{}#attpro#{}".format(colore, page)),
    ], [
        InlineKeyboardButton(text="⚽️ Attività Sportive", callback_data="catInfo#{}#attsport#{}".format(colore, page)),
    ], [
        InlineKeyboardButton(text="👥 Eventi / Riunioni", callback_data="catInfo#{}#eventi#{}".format(colore, page)),
    ], [
        InlineKeyboardButton(text="🏢 Uffici Pubblici", callback_data="catInfo#{}#uffici#{}".format(colore, page)),
    ], [
        InlineKeyboardButton(text="📄 Sanzioni", callback_data="catInfo#{}#sanzioni#{}".format(colore, page)),
        InlineKeyboardButton(text="🚗 Spostamenti", callback_data="catInfo#{}#sposta#{}".format(colore, page)),
    ], [
        InlineKeyboardButton(text="🎓 Università", callback_data="catInfo#{}#uni#{}".format(colore, page)),
        InlineKeyboardButton(text="👷 Lavoro", callback_data="catInfo#{}#lavoro#{}".format(colore, page)),
    ], [
        InlineKeyboardButton(text="😷 Mascherine", callback_data="catInfo#{}#mascherine#{}".format(colore, page)),
    ]])


def infoPages(colore: str, categoria: str, page: int=0, totPages: int=1):
    # Una pagina
    if totPages == 1:
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="↩️ Indietro", callback_data="infoColore#{}".format(colore))
        ]])
    # Più pagine, prima pagina
    elif page == 0:
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="➡️ Pag. {}".format(page+2), callback_data="catInfo#{}#{}#{}".format(colore, categoria, page+1))
        ], [
            InlineKeyboardButton(text="↩️ Indietro", callback_data="infoColore#{}".format(colore))
        ]])
    # Più pagine, ultima pagina
    elif (page + 1) == totPages:
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="⬅️ Pag. {}".format(page), callback_data="catInfo#{}#{}#{}".format(colore, categoria, page-1))
        ], [
            InlineKeyboardButton(text="↩️ Indietro", callback_data="infoColore#{}".format(colore))
        ]])
    # Più pagine, in mezzo
    else:
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="⬅️ Pag. {}".format(page), callback_data="catInfo#{}#{}#{}".format(colore, categoria, page-1)),
            InlineKeyboardButton(text="➡️ Pag. {}".format(page + 2), callback_data="catInfo#{}#{}#{}".format(colore, categoria, page+1))
        ], [
            InlineKeyboardButton(text="↩️ Indietro", callback_data="infoColore#{}".format(colore))
        ]])
