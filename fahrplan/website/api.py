import itertools
from urllib.request import urlopen
from .models import Post, User
from datetime import datetime, timedelta, date

from flask import json, jsonify, Blueprint

api = Blueprint("api", __name__, url_prefix="/api")

dummydata = True

# @api.route("/fahrplan")
# def getfahrplan():
#     return jsonify(Post.query.all())
    
# @api.get("/fahrplan/<nummer>")
# def getfahrplan(id):
#     data = get_fahrplan()
#     list=[]
#     for d in data:
#         id_list = d["bordpersonal"].split(",")
#         if id in id_list:
#             list.append(d)
#     return jsonify(list)

def get_fahrplan():
    return Post.query.all()

def get_sections():
    # if dummydata:
        js = open("website/dummydata/sections.json")
        data = json.load(js)
        list = []
        for d in data["sections"]:
            list.append(d)
        return list
    #else:
        #response = urlopen('http://localhost:5002/plan/get/rides')
        #data = json.loads(response.read())
        #return data
        

def get_fahrplan_id(id):
    data = get_fahrplan()
    for d in data["data"]:
        if id == d["id"]:
            return d


def get_zuege():
    if dummydata:
        js = open("website/dummydata/zuege.json")
        data = json.load(js)
        list = []
        for d in data["trains"]:
            list.append(d)
        return list
    else:
        response = urlopen('http://localhost:5002/api/zuege')
        # 'http://localhost:5002/get/zuege'
        # https://jsonplaceholder.typicode.com/posts
        data = json.loads(response.read())
        return data

def get_strecken():
    # if dummydata:
        #js = open("./dummydata/planned_routes.json")
        js = open("website/dummydata/planned_routes.json")
        data = json.load(js)
        list = []
        for d in data["data"]:
            list.append(d)
        return list
    #else:
        #response = urlopen('http://localhost:5002/plan/get/rides')
        #data = json.loads(response.read())
        #return data


def get_bordpersonal():
    # if dummydata:
        js = open("./dummydata/bordpersonal.json")
        data = json.load(js)
        return data

# def get_zug(id):
#     data = get_zuege()
#     for d in data["trains"]:
#         if id == d["id"]:
#             return d["name"]

def get_fahrplan_von_bordpersonal(id):
    data = get_fahrplan()
    # for d in data["data"]:
    for d in data:
        id_list = d["bordpersonal"].split(",")
        if id in id_list:
            return d

def get_preis_von_fahrtstrecke(id):
    data = get_sections()
    id_list = id.split(",")
    prize = 0
    for d in data:
        if str(d["id"]) in id_list:   
            prize = prize + d["fee"]        
    return prize

def get_dauer_von_fahrtstrecke(id):
    data = get_sections()
    id_list = id.split(",")
    dauer = 0
    for d in data:
        if str(d["id"]) in id_list:   
            dauer = dauer + (d["distance"]/d["maxSpeed"])        
    return dauer

def get_fahrten_von_bordpersonal(id):
    data = get_fahrplan()
    id = str(id)
    return_data = []
    for d in data:
        id_list = d.bordpersonal.split(",")
        if id in id_list:   
            return_data.append(d)       
    # return_data = Post.query.filter_by(author=id).all()
    return return_data

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

def get_station(id):
    js = open("website/dummydata/bhf.json")
    data = json.load(js)
    list = []
    for d in data["data"]:
        list.append(d)
    for l in list:
        if str(l["id"]) == str(id):
            return l["name"]
    
def get_spurweite(zug_name,s):
    
    if dummydata:
        js = open("website/dummydata/zuege.json")
        data = json.load(js)

        for d in data["trains"]:
        
            if str(d["name"]) == str(zug_name):
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

def get_spurweite2(s):
    strecken = get_strecken()
    s_list = s.split(",")
    list=[]
    for st in strecken:
        for i in s_list:
            if str(st["id"]) == str(i):
                list.append(str(st["spurweite"]))
    return list

def get_besetzt(zug,abfahrt,ankunft,datum):
    fahrten = get_fahrplan()
    for f in fahrten:
        if str(f.datum) == datum and str(f.zug) == zug:
            von = datetime.strptime(abfahrt, '%H:%M')
            bis = datetime.strptime(ankunft, '%H:%M')
            if datetime.strptime(f.uhrzeit, '%H:%M') <= von <= datetime.strptime(f.ankunft, '%H:%M'):
                if datetime.strptime(f.uhrzeit, '%H:%M') <= bis <= datetime.strptime(f.ankunft, '%H:%M'):
                    return True
    return False
