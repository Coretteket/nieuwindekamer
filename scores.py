import requests
import os
import time
import glob
import html
import math
import json
import re
import sys
import mysql.connector
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime
import urllib.parse
from random import seed
from random import random

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

print(pf(info) + "Starting scores.py...")

mydb = mysql.connector.connect(
    host="XXX",
    user="XXX",
    password="XXX",
    database="XXX"
)

cursor = mydb.cursor()
cursor.execute("SELECT * FROM hot_topics")
records = cursor.fetchall()

hots = []

for i in records:
    hots.append(i[1])

cursor = mydb.cursor()
cursor.execute("SELECT * FROM not_topics")
records = cursor.fetchall()

nots = []

for i in records:
    nots.append(i[1])

cursor = mydb.cursor()
cursor.execute("SELECT * FROM gevonden_woorden")
records = cursor.fetchall()

try:
    s = sys.argv[1]
except:
    s = int(int(datetime.utcnow().timestamp()))
seed(s)

words = {}

for i in records:

    # RANDOM
    rand = random()

    # HOT TOPIC
    hot = 1
    for j in hots:
        if j in i:
            hot = 1.1

    # NOT TOPIC
    no = 1
    for j in nots:
        if j in i[1]:
            no = .25
    if i[2] == "":
        no = .25
    if i[6] and "https://" not in i[6]:
        no = .25
    if not i[2]:
        no = .25
    if len(i[1]) < 6 and "." in i[1]:
        no = .25

    # LENGTH
    upper = 1
    first = True
    for j in i[1]:
        if not j.islower() and not first:
            upper -= .5
        elif not j.islower():
            first = False
    if upper < 0:
        upper = 0

    # DATE
    print(i[4])
    print(i[4].isocalendar()[0])
    datediff = datetime.today().isocalendar()[0] * 52 + datetime.today().isocalendar()[1] - i[4].isocalendar()[0] * 52 - i[4].isocalendar()[1] + 1
    print(datediff)

    # SCORE
    score = (rand * hot + upper) * no / (2.1 * math.sqrt(datediff))

    if i == "":
        score = -1

    words[i[1]] = round(score, 5)

    try:
        mycursor = mydb.cursor()
        sql = "UPDATE gevonden_woorden SET score = %s WHERE id = %s;"
        val = (round(score, 5), int(i[0]))
        mycursor.execute(sql, val)
        mydb.commit()
    except Exception as e:
        print(pf(err) + "Could not commit scores to database (" + e + ").")

print(pf(info) + "Committed " + str(len(words)) + " words' scores to the database.")

cursor = mydb.cursor()
cursor.execute("SELECT * from gevonden_woorden WHERE override > 0 AND getweet = 0 ORDER BY override ASC")
d1 = cursor.fetchall()

cursor = mydb.cursor()
cursor.execute("SELECT * from gevonden_woorden WHERE override = 0 AND getweet = 0 ORDER BY score DESC")
d2 = cursor.fetchall()

d = d1 + d2

msg = ""
counter = 0
for i in d:
    if counter < 10:
        msg += str(i[1]) + ", "
    counter += 1

print(pf(info) + "The next ten words are: "+ msg[:-2] + ".")