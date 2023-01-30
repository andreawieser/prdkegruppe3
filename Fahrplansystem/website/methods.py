from urllib.request import urlopen
from .models import Post
from datetime import datetime

from flask import json

dummydata = False

# Methode gibt alle Fahrdurchführungen zurück
def get_fahrplan():
    return Post.query.all()

# Methode gibt alle Sections der Dummydaten zurück
def get_sections():
    js = open("website/dummydata/sections.json")
    data = json.load(js)
    list = []
    for d in data["sections"]:
        list.append(d)
    return list
        
# Methode gibt den Fahrplan nach User Id zurück
def get_fahrplan_id(id):
    data = get_fahrplan()
    for d in data["data"]:
        if id == d["id"]:
            return d

# Methode gibt alle Züge des Flottensystems zurück, wenn die Variable Dummydaten auf False gesetzt ist
def get_zuege():
    if dummydata:
        js = open("website/dummydata/zuege2.json")
        data = json.load(js)
        list = []
        for d in data:
            list.append(d)
        return list
    else:     
        response = urlopen('http://127.0.0.1:5002/api/zuege-komp/')
        data = json.loads(response.read())
        return data

# Methode gibt alle vorhandenen Streckenabschnitte zurück(Dummydaten planned_routes) 
def get_strecken():
    js = open("website/dummydata/planned_routes.json")
    data = json.load(js)
    list = []
    for d in data["data"]:
        list.append(d)
    return list

# Methode gibt Dummydaten zu Testzwecken zurück
def get_bordpersonal():
        js = open("./dummydata/bordpersonal.json")
        data = json.load(js)
        return data

# Methode gibt die Fahrtdurchführungen einer Mitarbeiter Id zurück
def get_fahrplan_von_bordpersonal(id):
    data = get_fahrplan()
    for d in data:
        id_list = d["bordpersonal"].split(",")
        if id in id_list:
            return d

# Methode gibt den mindest Preis einer Fahrtdurchführung zurück
def get_preis_von_fahrtstrecke(id):
    data = get_sections()
    id_list = id.split(",")
    prize = 0
    for d in data:
        if str(d["id"]) in id_list:   
            prize = prize + d["fee"]        
    return prize

# Methode gibt die berrechnete Dauer für die Fahrt zurück
def get_dauer_von_fahrtstrecke(id):
    data = get_sections()
    id_list = id.split(",")
    dauer = 0
    for d in data:
        if str(d["id"]) in id_list:   
            dauer = dauer + (d["distance"]/d["maxSpeed"])        
    return dauer

# Methode gibt die Fahrten eines Bordpersonals nach Id zurück
def get_fahrten_von_bordpersonal(id):
    data = get_fahrplan()
    id = str(id)
    return_data = []
    for d in data:
        id_list = d.bordpersonal.split(",")
        if id in id_list:   
            return_data.append(d)       
    return return_data

# Methode gibt den Start Bhf der erstellten Strecke zurück
def get_start(i):
    data = get_strecken()
    starts = []
    id_list = i.split(",")
    for l in id_list:
        for d in data:
            if str(d["id"]) == str(l):
                starts.append(d["startStation"])
    ends = []
    for l in id_list:
        for d in data:
            if str(d["id"]) == str(l):
                ends.append(d["endStation"])

    for s in starts:
        if s not in ends:
            return s

# Methode prüft ob die erstellte Strecken möglich ist 
def is_kreis(i):
    data = get_strecken()
    starts = []
    ends = []
    id_list = i.split(",")
    for l in id_list:
        for d in data:
            if str(d["id"]) == str(l):
                starts.append(d["startStation"])
                ends.append(d["endStation"])

    s_list =[]
    e_list =[]
    for s in starts:
        if s not in ends:
            s_list.append(s)
    for e in ends:
        if e not in starts:
            e_list.append(e)
    
    if len(s_list) == 1:
        if len(e_list) == 1:
            return True
        return False
    else:
        return False

# Methode gibt den End Bhf der erstellten Strecke zurück
def get_end(i):
    data = get_strecken()
    starts = []
    ends = []
    id_list = i.split(",")
    
    for l in id_list:
        for d in data:
            if str(d["id"]) == str(l):
                ends.append(d["endStation"])
    for l in id_list:
        for d in data:
            if str(d["id"]) == str(l):
                starts.append(d["startStation"])

    for s in ends:
        if s not in starts:
            return s

# Methode gibt alle Haltestellen der Fahrtdruchführung zurück
def get_station(id):
    js = open("website/dummydata/bhf.json")
    data = json.load(js)
    list = []
    for d in data["data"]:
        list.append(d)
    for l in list:
        if str(l["id"]) == str(id):
            return l["name"]

# Methode prüft ob die Spurweite des Zugs und der Strecke übereinstimmen 
def get_spurweite(zug_name,s):
    
    if dummydata:
        js = open("website/dummydata/zuege2.json")
        data = json.load(js)

        for d in data:
        
            if str(d["zugnummer"]) == str(zug_name):
                for i in get_spurweite2(s):
                    if str(i) != str(d["spurweite"]):
                        return True
    else:
        data = get_zuege()
        for d in data:
            if str(d["zugnummer"]) == str(zug_name):
                for i in get_spurweite2(s):
                    if str(i) != str(d["spurweite"]):
                        return True
        
    return False

# Erweitert get_spurweite
def get_spurweite2(s):
    strecken = get_strecken()
    s_list = s.split(",")
    list=[]
    for st in strecken:
        for i in s_list:
            if str(st["id"]) == str(i):
                list.append(str(st["spurweite"]))
    return list

# Methode prüft ob der ausgewählte Zug verfügbar ist
def get_besetzt(zug,abfahrt,ankunft,datum):
    fahrten = get_fahrplan()
    for f in fahrten:
        if str(f.datum) == datum and str(f.zug) == zug:
            von = datetime.strptime(abfahrt, '%H:%M')
            bis = datetime.strptime(ankunft, '%H:%M')
            if datetime.strptime(f.uhrzeit, '%H:%M') <= von <= datetime.strptime(f.ankunft, '%H:%M'):
                return True
            if datetime.strptime(f.uhrzeit, '%H:%M') <= bis <= datetime.strptime(f.ankunft, '%H:%M'):
                return True
            if datetime.strptime(f.uhrzeit, '%H:%M') >= von:
                if datetime.strptime(f.ankunft, '%H:%M') <= bis:
                    return True
                if datetime.strptime(f.uhrzeit, '%H:%M') <= bis:
                    return True 
    return False

# Methode prüft ob das ausgewählte Bordpersonal verfügbar ist
def get_verfügabar_bordpersonal(bordpersonal,abfahrt,ankunft,datum):
    fahrten = get_fahrplan()
    b_list = bordpersonal.split(",")
    for f in fahrten:
        bo = f.bordpersonal
        bo_list = bo.split(",")
        for b in b_list:
            if str(f.datum) == datum and str(b) in bo_list:
                von = datetime.strptime(abfahrt, '%H:%M')
                bis = datetime.strptime(ankunft, '%H:%M')

                if datetime.strptime(f.uhrzeit, '%H:%M') <= von <= datetime.strptime(f.ankunft, '%H:%M'):
                    return True
                if datetime.strptime(f.uhrzeit, '%H:%M') <= bis <= datetime.strptime(f.ankunft, '%H:%M'):
                    return True
                if datetime.strptime(f.uhrzeit, '%H:%M') >= von:
                    if datetime.strptime(f.ankunft, '%H:%M') <= bis:
                        return True
                    if datetime.strptime(f.uhrzeit, '%H:%M') <= bis:
                        return True           
    return False

# Methode prüft ob der Zug verfügbar ist oder ob er zum gewählten Zeitpunkt gewartete wird
def get_wartung(zug,abfahrt,ankunft,datum):
    zuege = get_zuege()

    for z in zuege:
        if str(z["zugnummer"]) == str(zug):
            for w in z["wartungen"]:
                wartung_start = datetime.strptime(w["start"], '%H:%M')
                wartung_ende = datetime.strptime(w["ende"], '%H:%M')
                wartung_datum = datetime.strptime(w["datum"], '%Y-%m-%d').strftime('%d.%m.%y')
                von = datetime.strptime(abfahrt, '%H:%M')
                bis = datetime.strptime(ankunft, '%H:%M')

                if str(wartung_datum) == datum and str(z["zugnummer"]) == zug:
                    if wartung_start <= von <= wartung_ende:
                        return True
                    if wartung_start <= bis <= wartung_ende:
                        return True
                    if wartung_start >= von:
                        if wartung_ende <= bis:
                            return True
                        if wartung_start <= bis:
                            return True 
    return False




