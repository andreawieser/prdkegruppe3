import itertools
from urllib.request import urlopen

from flask import json

# True = Dummydaten werden verwendet
# False = Daten der anderen Applikationen werden verwendet

dummydata = True


# Geplante Fahrtdurchführungen werden von den Dummydaten geladen oder vom Fahrplansystem

def get_planned_routes():
    if dummydata:
        js = open("./dummydata/planned_routes.json")
        data = json.load(js)
        return data
    else:
        response = urlopen('http://127.0.0.1:5001/api/fahrplan')
        data = json.loads(response.read())
        return data


# Geplante Fahrtdurchführungen haben eine ID

def get_planned_route_by_id(id):
    data = get_planned_routes()
    for pr in data["data"]:
        if int(id) == pr["id"]:
            return pr


# Fahrtdurchführungen werden von den Dummydaten geladen oder vom Fahrplansystem

def get_rides():
    if dummydata:
        js = open("./dummydata/rides.json")
        data = json.load(js)
        return data
    else:
        response = urlopen('http://127.0.0.1:5001/api/fahrplan')
        data = json.loads(response.read())
        return data


# Fahrtdurchführungen haben eine ID

def get_ride_by_id(id):
    data = get_rides()
    for r in data["data"]:
        if id == r["id"]:
            return r


# Strecken werden von den Dummydaten geladen, da sie vom Streckensystem bereitgestellt werden würden

def get_routes():
    js = open("./dummydata/routes.json")
    data = json.load(js)
    return data


# Strecken haben eine ID

def get_route_id(name):
    routes = get_routes()
    for r in routes["routes"]:
        if r["name"] == name:
            return r["id"]


# Strecken haben einen Namen

def get_route_name():
    routes = get_routes()
    name = []
    for r in routes["routes"]:
        name.append(r["name"])
    return list(dict.fromkeys(name))


# Strecken-ID kann anhand der Linie gefunden werden

def get_route_id_by_sections(list_sections):
    routes = get_routes()
    for r in routes["routes"]:
        if all(elem in r["sections"] for elem in list_sections):
            return r


# Sucht die Strecke einer Fahrtdurchführung

def get_route_of_ride(id):
    planned_route = get_planned_route_by_id(int(id))
    sections_planned_route = list(planned_route["sections"])
    routes = []
    for s in sections_planned_route:
        section = get_section_by_id(s)
        for section_routes in section["routes"]:
            routes.append(section_routes)
    return set(routes)


# Linien werden von den Dummydaten geladen oder vom Fahrplansystem

def get_sections():
    if dummydata:
        js = open("./dummydata/sections.json")
        data = json.load(js)
        return data
    else:
        response = urlopen('http://127.0.0.1:5001/api/fahrplan')
        data = json.loads(response.read())
        return data


# Linien haben eine ID

def get_section_by_id(id):
    data = get_sections()
    for s in data["sections"]:
        if id == s["id"]:
            return s


# Linien befinden sich auf Strecken

def get_sections_by_route_id(id):
    data = get_sections()
    route = []
    for s in data["sections"]:
        if id == s["route"]:
            route.append(s["startStation"])
            route.append(s["endStation"])
    return list(k for k, _ in itertools.groupby(route))


# Züge werden von den Dummydaten geladen oder vom Flottensystem

def get_trains():
    if dummydata:
        js = open("dummydata/trains.json")
        data = json.load(js)
        return data
    else:
        response = urlopen('http://127.0.0.1:5002/api/zuege-komp/')
        data = json.loads(response.read())
        return data


# Züge haben eine ID

def get_train_by_id(id):
    data = get_trains()
    for t in data["trains"]:
        if id == t["id"]:
            return t


# Haltestellen werden von den Dummydaten geladen oder vom Fahrplansystem

def get_stations():
    if dummydata:
        js = open("./dummydata/stations.json")
        data = json.load(js)
        return data
    else:
        response = urlopen('http://127.0.0.1:5001/api/fahrplan')
        data = json.loads(response.read())
        return data


# Haltestellen haben eine ID

def get_station_by_id(id):
    stations = get_stations()
    for s in stations["stations"]:
        if s["id"] == id:
            return s


# Haltestellen haben einen Namen

def get_station():
    stations = get_stations()
    list_stations = []
    for s in stations["stations"]:
        list_stations.append(s["name"])
    return list_stations


# Haltestellen können nach dem Namen gesucht werden

def get_station_by_name(name):
    stations = get_stations()
    for s in stations["stations"]:
        if s["name"] == name:
            return s


# Warnungen werden von den Dummydaten geladen, da sie vom Streckensystem bereitgestellt werden würden

def get_warnings():
    js = open("./dummydata/warnings.json")
    data = json.load(js)
    return data


# Warnungen haben eine ID

def get_warning_by_id(id):
    data = get_warnings()
    for d in data["data"]:
        if id == d["id"]:
            return d
