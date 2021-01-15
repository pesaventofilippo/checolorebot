# Python Libraries
from time import sleep
from telepotpro import Bot, glance
from telepotpro.exception import TelegramError, BotWasBlockedError
from telepotpro.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from threading import Thread
from pony.orm import db_session, select
from datetime import datetime
from json import load as jsload
from os.path import abspath, dirname, join

# Custom Modules
from modules.database import User, Regione, Info
from modules import keyboards, helpers, api

with open(join(dirname(abspath(__file__)), "settings.json")) as settings_file:
    js_settings = jsload(settings_file)

bot = Bot(js_settings["token"])
updatesEvery = js_settings["updateEveryMin"]


@db_session
def runUpdates(now):
    data = api.getData()
    timestring = now.strftime("%H:%M")
    for region in select(r for r in Regione):
        region.color = data[region.name]
        region.updatedTime = timestring
    info = Info.get(id=1)
    info.data = api.getInfo()


@db_session
def runDailyUpdates(now):
    for user in select(u for u in User if u.wantsNotifications):
        userHour = user.dailyUpdatesTime.split(":")
        if int(userHour[0]) == now.hour and int(userHour[1]) == now.minute:
            try:
                if user.chatId < 0:
                    keys = keyboards.infoColorePvt(user.region.color)
                else:
                    keys = keyboards.infoColore(user.region.color)
                bot.sendMessage(user.chatId, "Buongiorno! 👋\n"
                                             "{} <b>{}</b> oggi è: {}.".format(helpers.getEmoji(user.region.color),
                                             user.region.name, user.region.color), parse_mode="HTML", reply_markup=keys)
            except (TelegramError, BotWasBlockedError):
                pass


@db_session
def reply(msg):
    chatId = msg['chat']['id']
    name = msg['from']['first_name']
    if "text" in msg:
        text = msg['text'].replace("@checolorebot", "")
    else:
        if chatId > 0:
            bot.sendMessage(chatId, "🤨 Media non supportati. /help")
        return

    if not User.exists(lambda u: u.chatId == chatId):
        User(chatId=chatId)
    user = User.get(chatId=chatId)


    if text == "/info":
        bot.sendMessage(chatId, "ℹ️ <b>Informazioni sul bot</b>\n"
                                "CheColoreBot è un bot creato e sviluppato da Filippo Pesavento, per risolvere il "
                                "problema di non sapere mai ogni giorno di che colore sia la propria regione.\n"
                                "Problemi dell'era covid...\n\n"
                                "- Sviluppo: <a href=\"https://t.me/pesaventofilippo\">Filippo Pesavento</a>\n"
                                "- Progetto OpenSource: <a href=\"https://github.com/pesaventofilippo/checolorebot\">GitHub</a>\n"
                                "- Fonte dati: <a href=\"http://www.governo.it/it/articolo/domande-frequenti-sulle-misure-adottate-dal-governo/15638\">Governo</a>\n"
                                "- Utenti attuali: <b>{}</b>".format(len(list(select(u for u in User)))),
                                parse_mode="HTML", disable_web_page_preview=True)

    elif text == "/help":
        bot.sendMessage(chatId, "Ciao, sono <b>CheColoreBot</b>! 👋🏻\n"
                                "Posso dirti di che \"colore\" sono le regioni ogni giorno e mandarti promemoria.\n\n"
                                "<b>Lista dei comandi</b>:\n"
                                "- /start - Colore regione\n"
                                "- /panoramica - Lista colore regioni\n"
                                "- /settings - Cambia impostazioni bot\n"
                                "- /info - Informazioni sul bot\n\n"
                                "<b>Nota:</b> Se in qualsiasi chat scrivi @checolorebot, posso mandare un messaggio già "
                                "pronto con le informazioni di una regione: comodo per far conoscere il bot ai tuoi amici!\n"
                                "Clicca il tasto qui sotto per provare!"
                                "", parse_mode="HTML", reply_markup=keyboards.tryInline())

    elif text.startswith("/broadcast ") and chatId in js_settings["admins"]:
        bdText = text.split(" ", 1)[1]
        pendingUsers = select(u.chatId for u in User)[:]
        userCount = len(pendingUsers)
        for u in pendingUsers:
            try:
                bot.sendMessage(u, bdText, parse_mode="HTML", disable_web_page_preview=True)
            except (TelegramError, BotWasBlockedError):
                userCount -= 1
        bot.sendMessage(chatId, "📢 Messaggio inviato correttamente a {0} utenti!".format(userCount))

    elif text == "/update" and chatId in js_settings["admins"]:
        runUpdates(datetime.now())
        bot.sendMessage(chatId, "✅ Aggiornamento completato!")

    elif text == "/users" and chatId in js_settings["admins"]:
        totalUsers = len(select(u for u in User)[:])
        bot.sendMessage(chatId, "👤 Utenti totali: <b>{}</b>".format(totalUsers), parse_mode="HTML")


    elif user.status != "normal":
        if text == "/annulla":
            if user.status == "selecting_region" and not user.region:
                bot.sendMessage(chatId, "Devi prima scegliere la tua regione!\n"
                                        "/setregion")
            else:
                user.status = "normal"
                bot.sendMessage(chatId, "Comando annullato!")

        elif user.status == "selecting_region":
            bot.sendMessage(chatId, "Benvenuto/a, <b>{}</b>!\n"
                                    "Scegli la tua regione:\n\n"
                                    "<i>Nota: il Trentino è diviso nelle province di Trento e Bolzano.</i>".format(name),
                            parse_mode="HTML", reply_markup=keyboards.regions())

    elif text == "/annulla":
        bot.sendMessage(chatId, "😴 Nessun comando da annullare!")


    elif text == "/start":
        if chatId < 0:
            keys = keyboards.infoColorePvt(user.region.color)
        else:
            keys = keyboards.infoColore(user.region.color)
        bot.sendMessage(chatId, "Benvenuto/a, <b>{}</b>!\n"
                                "{} <b>{}</b> oggi è: {}.\n"
                                "<i>Ultimo aggiornamento: {}</i>".format(name, helpers.getEmoji(user.region.color),
                                user.region.name, user.region.color, user.region.updatedTime), parse_mode="HTML", reply_markup=keys)

    elif text == "/panoramica":
        mess = "📊 <b>Panoramica regioni</b>"
        for color in helpers.getColors():
            regioni = select(r for r in Regione if r.color == color)[:]
            if regioni:
                mess += "\n\n{} Regioni di colore <b>{}</b>:".format(helpers.getEmoji(color), color)
                for regione in sorted(regioni, key=lambda r: r.name):
                    mess += "\n- {}".format(("<b>"+regione.name+"</b>") if user.region == regione else regione.name)
        bot.sendMessage(chatId, mess, parse_mode="HTML")

    elif text == "/settings":
        bot.sendMessage(chatId, "🛠 <b>Impostazioni</b>\n"
                                "Ecco le impostazioni del bot. Cosa vuoi modificare?",
                        parse_mode="HTML", reply_markup=keyboards.settings_menu())

    elif chatId > 0:
        if text.startswith("/start info_"):
            color = text.split("_", 1)[1]
            if color in helpers.getColors():
                bot.sendMessage(chatId, "{} Info sul colore <b>{}</b>:".format(helpers.getEmoji(color), color),
                                parse_mode="HTML", reply_markup=keyboards.categorieInfo(color))
            else:
                bot.sendMessage(chatId, "🤔 Info sul colore non trovate.")

        else:
            bot.sendMessage(chatId, "Non ho capito...\n"
                                    "Serve aiuto? Premi /help")


@db_session
def button_press(msg):
    try:
        chatId = msg['message']['chat']['id']
        msgId = msg['message']['message_id']
        msgIdent = (chatId, msgId)
    except KeyError:
        chatId = msg['from']['id']
        msgIdent = msg['inline_message_id']
    query_split = msg['data'].split("#", 1)
    button = query_split[0]
    data = query_split[1]
    user = User.get(chatId=chatId)


    if button == "settings":
        if data == "regione":
            bot.editMessageText(msgIdent, "Scegli la tua regione:\n\n"
                                          "<i>Nota: il Trentino è diviso nelle province di Trento e Bolzano.</i>",
                                parse_mode="HTML", reply_markup=keyboards.regions())

        elif data == "notifiche":
            bot.editMessageText(msgIdent, "<b>Le notifiche sono {}.</b>\n\n"
                                          "Vuoi che ti mandi una notifica ogni giorno con il colore della tua regione?"
                                          "".format("🔔 Attive" if user.wantsNotifications else "🔕 Spente"),
                                parse_mode="HTML", reply_markup=keyboards.notifiche())

        elif data == "orario":
            bot.editMessageText(msgIdent, "🕙 Orario notifiche giornaliere: {}".format(user.dailyUpdatesTime),
                                reply_markup=keyboards.orari())


    if button == "setregion":
        user.region = Regione.get(name=data)
        user.status = "normal"
        if chatId < 0:
            keys = keyboards.infoColorePvt(user.region.color)
        else:
            keys = keyboards.infoColore(user.region.color)
        bot.editMessageText(msgIdent, "Benvenuto/a! 👋\n"
                                      "{} <b>{}</b> oggi è: {}.\n"
                                      "<i>Ultimo aggiornamento: {}</i>".format(helpers.getEmoji(user.region.color),
                                      user.region.name, user.region.color, user.region.updatedTime),
                            parse_mode="HTML", reply_markup=keys)

    elif button == "notifTime":
        if data == "done":
            bot.editMessageText(msgIdent, "🕙 Nuovo orario notifiche: <b>{}</b>!".format(user.dailyUpdatesTime),
                                parse_mode="HTML", reply_markup=None)

        else:
            hoursplit = user.dailyUpdatesTime.split(":")
            h = hoursplit[0]
            m = hoursplit[1]
            if data == "plus":
                if m == "00":
                    m = "30"
                elif m == "30":
                    m = "00"
                    h = "0" if h == "23" else str(int(h) + 1)
            else:
                if m == "00":
                    m = "30"
                    h = "23" if h == "0" else str(int(h) - 1)
                elif m == "30":
                    m = "00"
            user.dailyUpdatesTime = "{0}:{1}".format(h, m)
            bot.editMessageText(msgIdent, "🕙 Orario notifiche giornaliere: {}".format(user.dailyUpdatesTime),
                                reply_markup=keyboards.orari())

    elif button == "notifToggle":
        if data == "done":
            txt = "🔔 Notifiche attivate!" if user.wantsNotifications else "🔕 Notifiche disattivate."
            bot.editMessageText(msgIdent, txt, parse_mode="HTML", reply_markup=None)

        else:
            if data == "on":
                user.wantsNotifications = True
            elif data == "off":
                user.wantsNotifications = False
            bot.editMessageText(msgIdent, "<b>Le notifiche sono {}.</b>\n\n"
                                          "Vuoi che ti mandi una notifica ogni giorno con il colore della tua regione?\n"
                                          "<b>Nota</b>: Se vuoi cambiare l'orario, usa /orario."
                                          "".format("🔔 Attive" if user.wantsNotifications else "🔕 Spente"),
                                          parse_mode="HTML", reply_markup=keyboards.notifiche())

    elif button == "infoColore":
        if data in helpers.getColors():
            bot.editMessageText(msgIdent, "{} Info sul colore <b>{}</b>:".format(helpers.getEmoji(data), data),
                                parse_mode="HTML", reply_markup=keyboards.categorieInfo(data))

        else:
            bot.sendMessage(chatId, "🤔 Info sul colore non trovate.")

    elif button == "catInfo":
        data_split = data.split("#")
        colore = data_split[0]
        categoria = data_split[1]
        page = int(data_split[2])

        pages = helpers.getInfo(colore, categoria)
        bot.editMessageText(msgIdent, pages[page], parse_mode="HTML",
                            disable_web_page_preview=True,
                            reply_markup=keyboards.infoPages(colore, categoria, page, len(pages)))


@db_session
def query(msg):
    queryId, chatId, queryString = glance(msg, flavor='inline_query')
    text = helpers.nameToId(queryString)
    regions = select(r for r in Regione)[:]

    results = [
        InlineQueryResultArticle(
            id="reg_{}".format(region.name),
            title=region.name,
            input_message_content=InputTextMessageContent(
                message_text="{} <b>{}</b> oggi è: {}.\n"
                             "<i>Ultimo aggiornamento: {}</i>".format(helpers.getEmoji(region.color),
                             region.name, region.color, region.updatedTime),
                parse_mode="HTML"
            ),
            reply_markup=keyboards.infoColorePvt(region.color),
            description="{} {}".format(helpers.getEmoji(region.color), region.color),
            thumb_url="https://pesaventofilippo.com/assets/images/projects/checolorebot.png"
        )
        for region in regions if text in helpers.nameToId(region.name)
    ]
    bot.answerInlineQuery(queryId, results, cache_time=3600, is_personal=False)


def accept_message(msg):
    Thread(target=reply, args=[msg]).start()

def accept_button(msg):
    Thread(target=button_press, args=[msg]).start()

def incoming_query(msg):
    Thread(target=query, args=[msg]).start()

bot.message_loop(
    callback={'chat': accept_message, 'callback_query': accept_button, 'inline_query': incoming_query}
)

while True:
    sleep(60)
    now = datetime.now()
    if now.minute % updatesEvery == 0:
        runUpdates(now)
        runDailyUpdates(now)
