from pony.orm import db_session

regionList = ["Abruzzo", "Basilicata", "Bolzano", "Calabria", "Campania", "Emilia-Romagna",
              "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche", "Molise",
              "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana", "Trento", "Umbria",
              "Valle d'Aosta", "Veneto"]

colorEmojis = {
    "rosso": "🔴",
    "arancione": "🟠",
    "giallo": "🟡",
    "verde": "🟢",
    "bianco": "⚪️",
    "n/a": "❓"
}

rules = {
    "giallo": {
        "attcom": "",
        "attpro": "",
        "attsport": "",
        "eventi": "",
        "uffici": "",
        "sanzioni": "",
        "sposta": "",
        "uni": "",
        "lavoro": "",
        "mascherine": ""
    },

    "arancione": {
        "attcom": "",
        "attpro": "",
        "attsport": "",
        "eventi": "",
        "uffici": "",
        "sanzioni": "",
        "sposta": "",
        "uni": "",
        "lavoro": "",
        "mascherine": ""
    },

    "rosso": {
        "attcom": "",
        "attpro": "",
        "attsport": "",
        "eventi": "",
        "uffici": "",
        "sanzioni": "",
        "sposta": "",
        "uni": "",
        "lavoro": "",
        "mascherine": ""
    }
}


def getEmoji(color: str):
    return colorEmojis[color] if color in colorEmojis else colorEmojis["n/a"]


def getColors():
    return [x.lower() for x in colorEmojis.keys() if x != "n/a"]


def nameToId(name: str):
    return name.lower().replace(" ", "").replace("-", "").replace("'", "")


def getInfo(color: str, category: str):
    from modules.database import Info
    with db_session:
        info = Info.get(id=1)
        raw = info.data
    try:
        res = raw[color][category]
    except KeyError:
        res = ""
    return res if res != "" else "🤔 Info non disponibili."
