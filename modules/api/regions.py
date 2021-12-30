from requests import get
from bs4 import BeautifulSoup
from modules.helpers import regionList, nameToId

baseUrl = "http://www.governo.it/it/articolo/domande-frequenti-sulle-misure-adottate-dal-governo/15638"

colori = {
    "#ffffff": "bianco",
    "#ffd732": "giallo"
}


def getData():
    resp = get(baseUrl)
    html = BeautifulSoup(resp.content, "lxml")
    data = {}
    for region in regionList:
        data[region] = "n/a"
        try:
            res = html.find("path", id=nameToId(region))
            if res:
                raw = res.attrs["fill"]
                data[region] = colori.get(raw, "n/a")
        except Exception:
            pass
    return data


def getInfo():
    resp = get(baseUrl)
    html = BeautifulSoup(resp.content, "lxml")

    ids = {
        "verde": "zona_verde",
        "bianco": "zona_bianca",
        "giallo": "zona_gialla",
        "arancione": "zona_arancione",
        "rosso": "zona_rossa"
    }

    tags = ["attcom", "eventi", "attsport", "uffici", "sanzioni",
            "sposta", "attpro", "uni", "mascherine", "lavoro"]

    data = {}
    for color in ids.keys():
        data[color] = {}
        try:
            container = html.find("div", id=ids[color])
            columns = container.findChildren("div", recursive=False)
    
            sections = []
            for col in columns:
                sections.extend(col.findChildren("div", recursive=False))
    
            tagIndex = 0
            for section in sections:
                try:
                    title = section.findChild("p", class_="titolo_faq", recursive=True).text
                    listaDomande = section.findChild("div", class_="accordion_content_faq", recursive=True)
                    listaDomande = listaDomande.findChildren("li")

                    pages = []
                    desc = "ℹ️ <b>{}</b>\n".format(title)
                    for domanda in listaDomande:
                        quest = str(domanda.strong.extract())
                        quest = quest.replace("<strong>", "").replace("</strong>", "").strip()
                        answer = str(domanda.text).strip()
                        parsed = "\n\n" \
                                "📌 <b>{}</b>\n" \
                                "👉 <i>{}</i>".format(quest, answer)
                        desc += parsed
                        if len(desc + parsed) > 2048:
                            pages.append(desc)
                            desc = ""

                    if desc:
                        pages.append(desc)
                    data[color][tags[tagIndex]] = pages
                except Exception:
                    data[color][tags[tagIndex]] = []
                finally:
                    tagIndex += 1

        except Exception:
            pass
    return data
