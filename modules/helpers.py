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


def getEmoji(color: str):
    return colorEmojis[color] if color in colorEmojis else colorEmojis["n/a"]


def getColors():
    return [x.lower() for x in colorEmojis.keys() if x != "n/a"]
