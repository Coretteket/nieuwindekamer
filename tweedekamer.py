import requests, os, os.path, time, glob, html, json, re, mysql.connector
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime
import urllib.parse

latestt = ""
latestf = ""
latestn = ""
ntitel = ""
nnaam = ""
nfractie = ""
timediff = ""
lastcount = 0

# LOGGING FUNCTIONS
warn = 1
err = 2
info = 3


def pf(type):
    if type == 1:
        return "[" + datetime.now().strftime("%H:%M:%S") + "] WARN: "
    elif type == 2:
        return "[" + datetime.now().strftime("%H:%M:%S") + "] ERROR: "
    elif type == 3:
        return "[" + datetime.now().strftime("%H:%M:%S") + "] INFO: "
    else:
        return ""


def urlencode(str):
    return urllib.parse.quote(str)


def tklookup(search):
    global ignore, latestt, latestn, latestf, lastcount, ntitel, nnaam, nfractie
    skipaanwezig = 0
    content = s.find("div", {"class": "content"})
    children = content.findChildren()
    search = search.replace("&", "&amp")
    ignore = False
    for count in range(len(children) - 1):
        if count < lastcount:
            continue
        i = children[count]
        motie = False
        if str(i).startswith("<p>Aanwezig zijn"):
            skipaanwezig = 1
            continue
        if skipaanwezig == 1:
            skipaanwezig = 2
            continue
        if skipaanwezig == 2:
            skipaanwezig = 0
            continue
        if str(i.parent).startswith('<div class="motie">'):
            motie = True
        if (
            str(i).startswith("<span")
            or str(i).startswith("<strong")
            or str(i).startswith("<div")
            or str(i).startswith("<h1")
            or str(i).startswith("<ul")
            or str(i).startswith("<hr")
        ):
            continue
        if str(i).startswith("<h2"):
            latestt = i.text
            latestn = ""
        if re.match(r"<p>.+<strong>.+<\/strong>.*?:<br/>.+", str(i)):
            i = str(i)
            latestn = re.sub(r"<p>.+<strong>(.+)<\/strong>.*?:<br\/{0,1}>.+", r"\1", i)
            if latestn == "voorzitter":
                latestn = voorzitter
            latestf = re.sub(r"<p>.+<strong>.+<\/strong>(.*?):<br\/{0,1}>.+", r"\1", i)
            if not latestf == "":
                latestf = latestf.replace(" (", "").replace(")", "")
        if str(i).startswith("<p"):
            j = str(i)
            j = re.sub(r"<p>.+<strong>.+<\/strong>.*?:<br/>(.+)", r"\1", j)
            j = re.sub("<.*?>", "", j).strip().replace("\n", "")
            j = re.sub(r"[\!\?\,\:\;\(\)\"\–\«\»\[\]\…]", "", j).lower()
            j = re.sub(r"[-\'\"\.]+\B", "", j)
            j = re.sub(r"\B[-\'\"]+", "", j)
            j = re.sub(r"nr\.", "nummer", j)
            if search in j and not latestn == "":
                lastcount = count
                ntitel = str(latestt)
                if motie:
                    found = False
                    while found == False:
                        count += 1
                        if str(children[count]).startswith(
                            "<p>Naar mij blijkt, wordt de indiening ervan voldoende ondersteund."
                        ):
                            ignore = True
                            return
                        elif str(children[count]).startswith(
                            "<p>De <strong>voorzitter</strong>:<br>Deze motie is voorgesteld door het lid"
                        ) or str(children[count]).startswith(
                            "<p>De <strong>voorzitter</strong>:<br/>Deze motie is voorgesteld door het lid"
                        ):
                            found = True
                            nfractie = ""
                            nnaam = re.sub(
                                r"\<p\>De \<strong\>voorzitter\<\/strong\>\:\<br\/\>Deze motie is voorgesteld door het lid (.+?)\..*",
                                r"\1",
                                str(children[count]),
                            )
                            return
                        elif str(children[count]).startswith(
                            "<p>De <strong>voorzitter</strong>:<br>Deze motie is voorgesteld door de leden"
                        ) or str(children[count]).startswith(
                            "<p>De <strong>voorzitter</strong>:<br/>Deze motie is voorgesteld door de leden"
                        ):
                            found = True
                            nfractie = ""
                            nnaam = re.sub(
                                r"\<p\>De \<strong\>voorzitter\<\/strong\>\:\<br\/\>Deze motie is voorgesteld door de leden (.+?), .*? en .*",
                                r"\1",
                                str(children[count]),
                            )
                            if nnaam.startswith("<p>"):
                                nnaam = re.sub(
                                    r"\<p\>De \<strong\>voorzitter\<\/strong\>\:\<br\/\>Deze motie is voorgesteld door de leden (.+?) en .*",
                                    r"\1",
                                    str(children[count]),
                                )
                            return
                else:
                    nnaam = str(latestn)
                    nfractie = str(latestf)
                return
    print(
        pf(err) + "Could not find the person who said " + search + " in the transcript."
    )


# STANDAARDWAARDEN
urls = []
new = False
url = ""
months = {
    "januari": 1,
    "februari": 2,
    "maart": 3,
    "april": 4,
    "mei": 5,
    "juni": 6,
    "juli": 7,
    "augustus": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "december": 12,
}

debug = False
db = True

print(pf(info) + "Starting nw.py...")

# SQL-CONNECTIE MAKEN
mydb = mysql.connector.connect(
    host="10.10.0.31",
    user="nieuwindekamer",
    password="W6t7fYujgCW_]Xnc",
    database="nieuwindekamer",
)

# OPEN DE LIJST VAN DE VORIGE URL-SCRAPE
f = open("urls.json", "r", encoding="utf-8")
oldurls = json.load(f)

# DOE OPNIEUW EEN URL-SCRAPE
page = requests.get(
    "https://www.tweedekamer.nl/kamerstukken/plenaire_verslagen", allow_redirects=True
)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.findAll("h3", {"class": "mt-0 mb-0"})
for i in results:
    a = i.find("a")
    urls.append(a["href"])

# KIJK OF ER EEN NIEUWE IN DE LIJST IS
newurls = []
for i in urls:
    if i not in oldurls:
        newurl = "https://www.tweedekamer.nl" + i
        newurls.append(newurl)

# SLA DE NIEUWE URL LIJST OP
if debug == False:
    with open("urls.json", "w", encoding="utf-8") as f:
        json.dump(urls, f, indent=4)

print(pf(info) + "Found " + str(len(newurls)) + " new debates.")

for url in reversed(newurls):
    lastcount = 0

    # HAAL DE NIEUWE PAGINA OP
    page = requests.get(url, allow_redirects=True)
    s = BeautifulSoup(page.content, "html.parser")

    # CHECK OF DE HANDELING AF IS
    lastp = s.find_all("p")[-1]
    if not lastp.text.startswith("Sluiting"):
        # newurls.pop(-1)

        print(
            pf(warn) + "Found transcript, but it was not finished yet. Handling anyway."
        )
        # with open('urls.json', 'w', encoding="utf-8") as f:
        #    json.dump(urls, f, indent=4)
        # break

    # VIND DAARVAN DE DATUM
    query = s.find("h1", {"id": "main-title"})
    query = re.sub("<.*?>", "", str(query)).strip().replace("\n", "")
    query = re.sub(" +", " ", query)
    year = int(re.sub(".+ ([0-9]+) ([a-z]+) (20[0-9][0-9])", r"\3", query))
    month = months[re.sub(".+ ([0-9]+) ([a-z]+) (20[0-9][0-9])", r"\2", query)]
    day = int(re.sub(".+ ([0-9]+) ([a-z]+) (20[0-9][0-9])", r"\1", query))

    datum = datetime(year, month, day)

    # if os.path.isfile('./tk/{}.json'.format(datum.strftime('%Y-%m-%d'))):
    #    print(pf(warn) + 'Debate has already been handled.')

    # hour = int(lastp.text[9:11])
    # minute = int(lastp.text[12:14])

    # datumtijd = datetime(year, month, day, hour, minute)

    # timepassed = datetime.now() - datumtijd

    # if timepassed.days*24 + timepassed.seconds/3600 <= 10:
    #    newurls.pop(-1)
    #    print(pf(warn) + 'Found transcript, but the debate is most likely not streamable yet.')
    #    with open('urls.json', 'w', encoding="utf-8") as f:
    #        json.dump(urls, f, indent=4)
    #    break

    # VIND DE <P>'s IN HTML, FILTER EN VOEG TOE AAN ARRAY
    p = s.find_all("p")
    t = []
    pars = {}
    voorzitter = ""
    skipaanwezig = 0
    for i in p:
        i = html.unescape(str(i))
        i = re.sub(r"<p>.+<strong>.+<\/strong>.*:<br/>(.+)", r"\1", i)
        if i.startswith("<p><strong>Voorzitter:"):
            voorzitter = i.replace("<p><strong>Voorzitter: ", "").replace(
                "</strong></p>", ""
            )
            continue
        if i.startswith("<p>Aanwezig zijn"):
            skipaanwezig = 1
            continue
        if skipaanwezig == 1:
            skipaanwezig = 2
            continue
        if skipaanwezig == 2:
            skipaanwezig = 0
            continue
        i = re.sub(r"nr\.", "nummer", i)
        i = re.sub(r"[\!\?\,\:\;\(\)\"\–\«\»\[\]\…]", "", i).lower()
        i = re.sub(r"[-\'\"\.]+\B", "", i)
        i = re.sub(r"\B[-\'\"]+", "", i)
        t.append(re.sub("<.*?>", "", str(i)).strip().replace("  ", " "))

    text = " ".join(t)
    arr = text.split()

    # SLA HET TEKSTBESTAND OP
    if debug == False:
        with open(
            "tk-txt/{}.txt".format(datum.strftime("%Y-%m-%d")), "w", encoding="utf-8"
        ) as f:
            f.write(text)

    # VIND EN TEL UNIEKE WOORDEN IN ARRAY
    nh = {}
    for i in arr:
        if not (any(char.isdigit() for char in i) or i == ""):
            if not i == "nr" and not i in nh:
                nh[i] = 1
            else:
                nh[i] += 1

    newcorpus = Counter(nh)

    # MAAK DE TK-CORPUS UIT DAG-CORPI
    f = open("w.json", "r", encoding="utf-8")
    w = json.load(f)
    obcorpus = Counter(w)
    tkcorpus = Counter()
    for file in glob.glob("tk/*.json"):
        f = open(file, "r")
        new = json.load(f)
        newcounter = Counter(new)
        tkcorpus += newcounter

    # VIND KANDIDAAT-WOORDEN
    corpus = tkcorpus + obcorpus
    kw = newcorpus - corpus

    for i in list(kw):
        if "/" in i:
            del kw[i]

    # CHECK OF DE KANDIDAAT-WOORDEN NIEUW ZIJN
    nw = {}
    for i in kw:
        if i not in corpus:
            nw[i] = kw[i]

    # SLA DE NIEUWE DAG-CORPUS OP
    if debug == False:
        with open(
            "tk/{}.json".format(datum.strftime("%Y-%m-%d")), "w", encoding="utf-8"
        ) as f:
            json.dump(dict(newcorpus.most_common()), f, indent=4)

    # SLA WOORD VOOR WOORD OP IN DATABASE
    errcount = 0
    for i in nw:
        tklookup(i)
        if not ignore:
            if db:
                try:
                    mycursor = mydb.cursor()
                    highlighturl = url + "#:~:text=" + i
                    sql = "INSERT INTO gevonden_woorden (woord, gevonden_op, uitgesproken_op, frequentie, debatgemist_titel, tweedekamer_link, gezegd_door_naam, gezegd_door_fractie) VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s)"
                    val = (
                        i,
                        datum.strftime("%Y-%m-%d"),
                        nw[i],
                        ntitel,
                        highlighturl,
                        nnaam,
                        nfractie,
                    )
                    mycursor.execute(sql, val)
                    mydb.commit()
                except Exception as e:
                    if errcount > -1:
                        errcount += 1
                    if errcount < 4:
                        print(
                            pf(err)
                            + "Failed to commit the word '"
                            + i
                            + "' to the database ("
                            + str(e)
                            + ")."
                        )
                    else:
                        errcount = -1
                        print(
                            pf(err)
                            + "Final message; still failing to commit words to the database."
                        )

    print(
        pf(info)
        + "Converted transcript and added "
        + str(len(nw))
        + " new words to the database."
    )

mycursor = mydb.cursor()
sql = "UPDATE gevonden_woorden gv, twitter_handles th SET gv.gezegd_door_twitter=th.handle WHERE gv.gezegd_door_naam=th.naam AND gv.gezegd_door_twitter IS NULL;"
mycursor.execute(sql)
mydb.commit()

mycursor = mydb.cursor()
sql = "UPDATE gevonden_woorden gv, twitter_handles th SET gv.gezegd_door_fractie=th.partij WHERE gv.gezegd_door_naam=th.naam AND gv.gezegd_door_fractie = '';"
mycursor.execute(sql)
mydb.commit()
