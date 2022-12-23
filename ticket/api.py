import itertools
from urllib.request import urlopen

from flask import json

dummydata = True


def get_ride_by_id(id):
    data = get_rides()
    for r in data["data"]:
        if id == r["id"]:
            return r


def get_rides():
    if dummydata:
        js = open("./dummydata/rides.json")
        data = json.load(js)
        return data
    else:
        response = urlopen('http://localhost:5002/plan/get/rides')
        data = json.loads(response.read())
        return data


def get_routes():
    if dummydata:
        js = open("./dummydata/routes.json")
        data = json.load(js)
        return data
    else:
        response = urlopen('http://localhost:5003/routes/get')
        data = json.loads(response.read())
        return data


def get_route_name():
    routes = get_routes()
    name = []
    for r in routes["routes"]:
        name.append(r["name"])
    return list(dict.fromkeys(name))


def get_route_id_by_name(name):
    routes = get_routes()
    for r in routes["routes"]:
        if r["name"] == name:
            return r["id"]


def get_route_name_by_id(route_id):
    routes = get_routes()
    for r in routes["routes"]:
        if int(r["id"]) == int(route_id):
            return r["name"]


def get_route_id_by_sections(list_sections):
    routes = get_routes()
    for r in routes["routes"]:
        if all(elem in r["sections"] for elem in list_sections):
            return r


def get_planned_routes():
    if dummydata:
        js = open("./dummydata/planned_routes.json")
        data = json.load(js)
        return data
    else:
        response = urlopen('http://localhost:5002/plan/get/planned_routes')
        data = json.loads(response.read())
        return data


def get_planned_route_by_id(id):
    data = get_planned_routes()
    for pr in data["data"]:
        if int(id) == pr["id"]:
            return pr


def get_route_of_ride(id):
    planned_route = get_planned_route_by_id(int(id))
    sections_planned_route = list(planned_route["sections"])
    routes = []
    for s in sections_planned_route:
        section = get_section_by_id(s)
        for section_routes in section["routes"]:
            routes.append(section_routes)
    return set(routes)


def get_sections():
    if dummydata:
        js = open("./dummydata/sections.json")
        data = json.load(js)
        return data
    else:
        response = urlopen('http://localhost:5003/sections/get')
        data = json.loads(response.read())
        return data


def get_trains():
    if dummydata:
        js = open("./dummydata/trains.json")
        data = json.load(js)
        return data
    else:
        response = urlopen('http://localhost:5003/trains')
        data = json.loads(response.read())
        return data


def get_station():
    stations = get_stations()
    list_stations = []
    for s in stations["stations"]:
        list_stations.append(s["name"])
    return list_stations


def get_station_by_id(id):
    stations = get_stations()
    for s in stations["stations"]:
        if s["id"] == id:
            return s


def get_station_by_name(name):
    stations = get_stations()
    for s in stations["stations"]:
        if s["name"] == name:
            return s


def get_stations():
    if dummydata:
        js = open("./dummydata/stations.json")
        data = json.load(js)
        return data
    else:
        response = urlopen('http://localhost:5003/stations/get')
        data = json.loads(response.read())
        return data


def get_sections_by_route_id(id):
    data = get_sections()
    route = []
    for s in data["sections"]:
        if id == s["route"]:
            route.append(s["startStation"])
            route.append(s["endStation"])
    return list(k for k, _ in itertools.groupby(route))


def get_section_by_id(id):
    data = get_sections()
    for s in data["sections"]:
        if id == s["id"]:
            return s


def get_train_by_id(id):
    data = get_trains()
    for t in data["trains"]:
        if id == t["id"]:
            return t


def get_warnings():
    if dummydata:
        js = open("./dummydata/warnings.json")
        data = json.load(js)
        return data
    else:
        response = urlopen('http://localhost:5003/warnings/get')
        data = json.loads(response.read())
        return data
