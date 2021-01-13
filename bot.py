# Python Libraries
from time import sleep
from telepotpro import Bot
from telepotpro.exception import TelegramError, BotWasBlockedError
from threading import Thread
from pony.orm import db_session, select
from datetime import datetime
from json import load as jsload
from os.path import abspath, dirname, join

# Custom Modules
from modules.database import User, Regione
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


@db_session
def runDailyUpdates(now):
    for user in select(u for u in User if u.wantsNotifications):
        userHour = user.dailyUpdatesTime.split(":")
        if int(userHour[0]) == now.hour and int(userHour[1]) == now.minute:
            try:
                bot.sendMessage(user.chatId, "Buongiorno! 👋\n"
                                             "{} <b>{}</b> oggi è: {}.".format(helpers.getEmoji(user.region.color),
                                             user.region.name, user.region.color), parse_mode="HTML")
            except (TelegramError, BotWasBlockedError):
                pass


@db_session
def reply(msg):
    chatId = msg['chat']['id']
    name = msg['from']['first_name']
    if "text" in msg:
        text = msg['text']
    else:
        bot.sendMessage(chatId, "🤨 Media non supportati. /help")
        return

    if chatId < 0:
        return

    if not User.exists(lambda u: u.chatId == chatId):
        User(chatId=chatId)
    user = User.get(chatId=chatId)


    if text == "/about":
        bot.sendMessage(chatId, "ℹ️ <b>Informazioni sul bot</b>\n"
                                "CheColoreBot è un bot creato e sviluppato da Filippo Pesavento, per risolvere il "
                                "problema di non sapere mai ogni giorno di che colore sia la propria regione.\n"
                                "Problemi dell'era covid...\n\n"
                                "<b>Sviluppo:</b> <a href=\"https://t.me/pesaventofilippo\">Filippo Pesavento</a>\n"
                                "<b>Hosting:</b> Filippo Pesavento", parse_mode="HTML", disable_web_page_preview=True)

    elif text == "/help":
        bot.sendMessage(chatId, "Ciao, sono <b>CheColoreBot</b>! 👋🏻\n"
                                "Posso dirti di che \"colore\" sono le regioni ogni giorno e mandarti promemoria.\n\n"
                                "<b>Lista dei comandi</b>:\n"
                                "- /start - Colore regione\n"
                                "- /setregion - Scegli/Cambia regione\n"
                                "- /orario - Scegli orario notifiche\n"
                                "- /notifiche - Attiva/Disattiva notifiche\n"
                                "- /about - Informazioni sul bot\n"
                                "- /annulla - Annulla comando"
                                "", parse_mode="HTML")

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
        bot.sendMessage(chatId, "✅ Aggiornamento globale completato!")

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
        bot.sendMessage(chatId, "Benvenuto/a, <b>{}</b>!\n"
                                "{} <b>{}</b> oggi è: {}.\n"
                                "<i>Ultimo aggiornamento: {}</i>".format(name, helpers.getEmoji(user.region.color),
                                user.region.name, user.region.color, user.region.updatedTime), parse_mode="HTML")

    elif text == "/setregion":
        bot.sendMessage(chatId, "Scegli la tua regione:\n\n"
                                "<i>Nota: il Trentino è diviso nelle province di Trento e Bolzano.</i>",
                        parse_mode="HTML", reply_markup=keyboards.regions())

    elif text == "/notifiche":
        bot.sendMessage(chatId, "<b>Le notifiche sono {}.</b>\n\n"
                                "Vuoi che ti mandi una notifica ogni giorno con il colore della tua regione?\n"
                                "<b>Nota</b>: Se vuoi cambiare l'orario, usa /orario."
                                "".format("🔔 Attive" if user.wantsNotifications else "🔕 Spente"),
                        parse_mode="HTML", reply_markup=keyboards.notifiche())

    elif text == "/orario":
        if user.wantsNotifications:
            bot.sendMessage(chatId, "🕙 Orario notifiche giornaliere: {}".format(user.dailyUpdatesTime),
                            reply_markup=keyboards.orari())
        else:
            bot.sendMessage(chatId, "Hai disattivato le notifiche!\n"
                                    "Usa /notifiche per attivarle.")

    else:
        bot.sendMessage(chatId, "Non ho capito...\n"
                                "Serve aiuto? Premi /help")


@db_session
def button_press(msg):
    chatId = msg['message']['chat']['id']
    msgId = msg['message']['message_id']
    query_split = msg['data'].split("#", 1)
    button = query_split[0]
    data = query_split[1]
    user = User.get(chatId=chatId)

    if button == "setregion":
        user.region = Regione.get(name=data)
        user.status = "normal"
        bot.editMessageText((chatId, msgId), "Benvenuto/a! 👋\n"
                                             "{} <b>{}</b> oggi è: {}.\n"
                                             "<i>Ultimo aggiornamento: {}</i>".format(helpers.getEmoji(user.region.color),
                                             user.region.name, user.region.color, user.region.updatedTime),
                            parse_mode="HTML", reply_markup=None)

    elif button == "notifTime":
        if data == "done":
            bot.editMessageText((chatId, msgId), "🕙 Nuovo orario notifiche: <b>{}</b>!".format(user.dailyUpdatesTime),
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
            bot.editMessageText((chatId, msgId), "🕙 Orario notifiche giornaliere: {}".format(user.dailyUpdatesTime),
                                reply_markup=keyboards.orari())

    elif button == "notifToggle":
        if data == "done":
            txt = "🔔 Notifiche attivate!" if user.wantsNotifications else "🔕 Notifiche disattivate."
            bot.editMessageText((chatId, msgId), txt, parse_mode="HTML", reply_markup=None)

        else:
            if data == "on":
                user.wantsNotifications = True
            elif data == "off":
                user.wantsNotifications = False
            bot.editMessageText((chatId, msgId), "<b>Le notifiche sono {}.</b>\n\n"
                                    "Vuoi che ti mandi una notifica ogni giorno con il colore della tua regione?\n"
                                    "<b>Nota</b>: Se vuoi cambiare l'orario, usa /orario."
                                    "".format("🔔 Attive" if user.wantsNotifications else "🔕 Spente"),
                                    parse_mode="HTML", reply_markup=keyboards.notifiche())


def accept_message(msg):
    Thread(target=reply, args=[msg]).start()

def accept_button(msg):
    Thread(target=button_press, args=[msg]).start()

bot.message_loop(
    callback={'chat': accept_message, 'callback_query': accept_button}
)

while True:
    sleep(60)
    now = datetime.now()
    if now.minute % updatesEvery == 0:
        runUpdates(now)
        runDailyUpdates(now)
