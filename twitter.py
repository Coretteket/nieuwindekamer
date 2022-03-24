import tweepy
import mysql.connector
import datetime
import urllib
from random import seed
from random import randint
from random import shuffle
import datetime
from sys import exit

debug = False
tag = True
counter = 0
max = 1

# LOGGING FUNCTIONS
warn = 1
err = 2
info = 3


def pf(type):
    if type == 1:
        return "[" + datetime.datetime.now().strftime("%H:%M:%S") + "] WARN: "
    elif type == 2:
        return "[" + datetime.datetime.now().strftime("%H:%M:%S") + "] ERROR: "
    elif type == 3:
        return "[" + datetime.datetime.now().strftime("%H:%M:%S") + "] INFO: "
    else:
        return ""


consumer_key = "XXX"
consumer_secret = "XXX"
access_token = "XXX"
access_token_secret = "XXX"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

mydb = mysql.connector.connect(host="XXX", user="XXX", password="XXX", database="XXX")

week = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
maand = [
    " januari",
    " februari",
    " maart",
    " april",
    " mei",
    " juni",
    " juli",
    " augustus",
    " september",
    " oktober",
    " november",
    " december",
]

zinger1 = [
    "Een primeur ",
    "Een novum ",
    "Nieuw ",
    "Een nieuw woord ",
    "Kleurrijk taalgebruik ",
    "Nooit eerder ",
]
zinger2 = [
    "in Den Haag: ",
    "op het Binnenhof: ",
    "in de politiek: ",
    "in de Tweede Kamer: ",
]

blok1 = [
    "het woord “<<WOORD>>”",
    "door <<NAAM>>",
    "<<AFGELOPEN>> <<DATUM>>",
]

blok2 = [
    "voor het eerst",
    "plenair <<GEBRUIKT>>",
    "in de Tweede Kamer.",
]

cursor = mydb.cursor()
cursor.execute(
    "SELECT * from gevonden_woorden WHERE override > 0 AND getweet = 0 ORDER BY override ASC"
)
d1 = cursor.fetchall()

cursor = mydb.cursor()
cursor.execute(
    "SELECT * from gevonden_woorden WHERE override = 0 AND getweet = 0 ORDER BY score DESC"
)
d2 = cursor.fetchall()

d = d1 + d2

print(d1)

for i in range(len(d)):
    seed(d[i][0])
    counter += 1

    debat = d[i][7]

    if d[i][2]:
        woord = d[i][2]
    else:
        woord = d[i][1]

    if d[i][12] != "-" and d[i][12] != None:
        if tag == False:
            naam = d[i][12].replace("@", "@ ")
        else:
            naam = d[i][12]
    else:
        naam = "#" + d[i][10].replace(" ", "")

    fbnaam = d[i][10]

    if d[i][11] and not d[i][11] == d[i][10]:
        naam += " (" + d[i][11] + ")"
        fbnaam += " (" + d[i][11] + ")"

    days = (datetime.date.today() - d[i][4]).days
    if days <= 1:
        datumtype = -1
        datum = "gisteren"
    elif days <= 2 and randint(0, 2) >= 1:
        datumtype = -1
        datum = "eergisteren"
    elif days < 7:
        datumtype = 0
        datum = week[d[i][4].weekday()]
    else:
        datumtype = 1
        datum = str(d[i][4].day) + maand[d[i][4].month - 1]

    tweet = zinger1[randint(0, len(zinger1) - 1)]
    tweet += zinger2[randint(0, len(zinger2) - 1)]
    tweet += " ".join(shuffle(blok1))
    tweet += " ".join(shuffle(blok2))

    tweet = tweet.replace("<<WOORD>>", woord)
    tweet = tweet.replace("<<DATUM>>", datum)

    if randint(0, 3) < 3:
        tweet = tweet.replace("<<EERSTE>>", "eerste")
    else:
        tweet = tweet.replace("<<EERSTE>>", "allereerste")

    if randint(0, 1) < 1:
        tweet = tweet.replace("voor het eerst", "voor de eerste keer")

    if randint(0, 2) < 1:
        tweet = tweet.replace("in de Tweede Kamer", "in het parlement")

    if datumtype == -1:
        tweet = tweet.replace("<<AFGELOPEN>>", "").replace("  ", " ")
    elif datumtype == 1:
        if randint(0, 2) < 2 and not tweet.startswith("<<AFGELOPEN>>"):
            tweet = tweet.replace("<<AFGELOPEN>>", "op")
        else:
            tweet = tweet.replace("<<AFGELOPEN>>", "afgelopen")
    elif randint(0, 1) < 1:
        tweet = tweet.replace("<<AFGELOPEN>>", "").replace("  ", " ")
    else:
        tweet = tweet.replace("<<AFGELOPEN>>", "afgelopen")

    match randint(0, 4):
        case 0:
            tweet = tweet.replace("<<GEBRUIKT>>", "gebruikt")
        case 1:
            tweet = tweet.replace("<<GEBRUIKT>>", "gezegd")
        case 2:
            tweet = tweet.replace("<<GEBRUIKT>>", "uitgesproken")
        case 3:
            tweet = tweet.replace("<<GEBRUIKT>>", "geuit")
        case 4:
            tweet = tweet.replace("<<GEBRUIKT>>", "verwoord")

    if tweet[0] == " ":
        tweet = tweet[1:]

    if tweet[0].islower():
        tweet = tweet[0].capitalize() + tweet[1:]

    post = tweet.replace("<<NAAM>>", fbnaam)
    tweet = tweet.replace("<<NAAM>>", naam)

    if tweet.startswith("@"):
        tweet = "." + tweet

    print(pf(info) + 'Sent tweet: "' + tweet + '".')

    tweetlink = tweet + "\nhttps://nieuwindekamer.nl/n/" + urllib.parse.quote(d[i][1])

    post = post.replace("“", "'").replace("”", "'")
    tweet = tweet.replace("“", "'").replace("”", "'")

    if debug == False:
        api.update_status(tweetlink)

        try:
            mycursor = mydb.cursor()
            sql = (
                'UPDATE gevonden_woorden gv SET gv.getweet=1, gv.tweet = "'
                + tweet
                + '", gv.post = "'
                + post
                + '", gv.tweet_datum = NOW() WHERE gv.woord="'
                + d[i][1]
                + '";'
            )
            mycursor.execute(sql)
            mydb.commit()
        except Exception as e:
            print(pf(err) + "Couldn't update database entry for tweet.")

    if counter >= max and not max == -1:
        exit(0)
