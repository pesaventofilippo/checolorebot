from requests import get
from bs4 import BeautifulSoup
from modules.helpers import regionList, getColors


def getData():
    resp = get("http://www.governo.it/it/articolo/domande-frequenti-sulle-misure-adottate-dal-governo/15638")
    html = BeautifulSoup(resp.content, "lxml")
    data = {}
    for region in regionList:
        data[region] = "n/a"
        regName = region.replace(" ", "").replace("-", "").replace("'", "").lower()
        res = html.find("path", id=regName)
        if res:
            raw = res.attrs["onclick"]
            for color in getColors():
                if color in raw:
                    data[region] = color
    return data
