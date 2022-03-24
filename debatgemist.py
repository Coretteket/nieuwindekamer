import requests, os, time, glob, html, json, re, mysql.connector
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime
import urllib.parse

dbgwoord = ""
dbglink = ""
dbgcontext = ""
ntitel = ""
nnaam = ""
nfractie = ""

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


def debatgemist(i, date):
    global dbgwoord, dbglink, ntitel, dbgcontext, nnaam, nfractie
    i = i.replace("&", "%26")
    i = i.replace("#", "")
    i = i.replace("’", "'")
    a = f"https://debatgemist.tweedekamer.nl/zoeken?search_api_views_fulltext={urlencode(i)}&f[0]=created:[{date.strftime('%Y')}-{date.strftime('%m')}-{date.strftime('%d')}T00:00:00Z%20TO%20{date.strftime('%Y')}-{date.strftime('%m')}-{str(int(date.strftime('%d')) + 1)}T00:00:00Z]&f[1]=field_debate_type:154188"
    searchpage = requests.get(a, allow_redirects=True)
    dbg = BeautifulSoup(searchpage.content, "html.parser")

    blocks = dbg.find_all("article", {"class": "video_video-block"})
    if not blocks == "":
        dbgwoord = ""
        dbglink = ""
        dbgcontext = ""
        for j in reversed(blocks):
            find = j.find("div", {"class": "data"}).find(
                "div", {"class": "list-overview atblock__panel"}
            )
            if find:
                li = find.ul.find_all("li")
                for k in li:
                    try:
                        if i == k.strong.string.lower():
                            if k.strong in k.a:
                                continue
                            dbglink = str(k.a["href"])
                            dbgwoord = str(k.strong.string)
                            context = (
                                re.sub(r"\<a.+\<\/a\>", "", str(k).replace("\n", ""))
                                .replace("<li>", "")
                                .replace("</li>", "")
                            )
                            dbgcontext = str(" ".join(context.split())).replace(
                                '"', "'"
                            )
                            return
                    except:
                        print(pf(err) + "'NoneType' object has no attribute 'string'")


print(pf(info) + "Starting dg.py...")

mydb = mysql.connector.connect(
    host="XXX",
    user="XXX",
    password="XXX",
    database="XXX",
)

mycursor = mydb.cursor()
sql = (
    "select * from gevonden_woorden WHERE DATE_SUB('"
    + datetime.today().strftime("%Y-%m-%d")
    + "', INTERVAL 5 DAY) <= uitgesproken_op AND debatgemist_woord = '' OR debatgemist_woord IS NULL ORDER BY gevonden_op DESC;"
)
mycursor.execute(sql)
myresult = mycursor.fetchall()

errcount = 0
counter = 0
for i in myresult:
    debatgemist(i[1], i[4])
    if not dbgwoord == "":
        counter += 1
        try:
            mycursor = mydb.cursor()
            sql = 'UPDATE gevonden_woorden gv SET gv.debatgemist_woord="{}", gv.debatgemist_link="{}", gv.debatgemist_context="{}" WHERE gv.woord="{}";'.format(
                dbgwoord, dbglink, dbgcontext, i[1]
            )
            mycursor.execute(sql)
            mydb.commit()
        except Exception as e:
            if errcount > -1:
                errcount += 1
            if errcount < 4:
                print(
                    pf(err)
                    + f"Failed to commit the word '{i}' to the database. Error: {e}"
                )
            else:
                errcount = -1
                print(
                    pf(err)
                    + "Final message; still failing to commit words to the database."
                )
                raise

print(
    pf(info) + "Succesfully beautified " + str(counter) + " new words in the database."
)
