from requests import get
from bs4 import BeautifulSoup
from modules.helpers import regionList, getColors, nameToId

baseUrl = "http://www.governo.it/it/articolo/domande-frequenti-sulle-misure-adottate-dal-governo/15638"


def getData():
    resp = get(baseUrl)
    html = BeautifulSoup(resp.content, "lxml")
    data = {}
    for region in regionList:
        data[region] = "n/a"
        res = html.find("path", id=nameToId(region))
        if res:
            raw = res.attrs["onclick"]
            for color in getColors():
                if color in raw:
                    data[region] = color
    return data


def getInfo():
    resp = get(baseUrl)
    html = BeautifulSoup(resp.content, "lxml")

    ids = {
        "giallo": "zona_gialla",
        "arancione": "zona_arancione",
        "rosso": "zona_rossa"
    }

    tags = ["attcom", "eventi", "attsport", "uffici", "sanzioni",
            "sposta", "attpro", "uni", "mascherine", "lavoro"]

    data = {}
    for color in ids.keys():
        data[color] = {}
        container = html.find("div", id=ids[color])
        columns = container.findChildren("div", recursive=False)

        sections = []
        for col in columns:
            sections.extend(col.findChildren("div", recursive=False))

        tagIndex = 0
        for section in sections:
            title = section.findChild("p", class_="titolo_faq", recursive=True).text
            listaDomande = section.findChild("div", class_="accordion_content_faq", recursive=True)
            listaDomande = listaDomande.findChildren("li")

            desc = "ℹ️ <b>{}</b>\n".format(title)
            for domanda in listaDomande:
                quest = str(domanda.strong.extract())
                quest = quest.removeprefix("<strong>").removesuffix("</strong>").strip()
                answer = str(domanda.text).strip()
                desc += "\n\n" \
                        "📌 <b>{}</b>\n" \
                        "{}".format(quest, answer)

            data[color][tags[tagIndex]] = desc
            tagIndex += 1

    return data


getInfo()
