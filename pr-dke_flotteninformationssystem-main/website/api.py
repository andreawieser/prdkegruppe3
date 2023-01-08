from flask import Blueprint, jsonify
from website.models import Zug, Wartung

api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/zuege")
def getZuege():
    zuege = Zug.query.all()
    spurweite = 0
    zuege_list = []

    for zug in zuege:
        personenwaggons = []
        for waggon in zug.waggons:
            if waggon.__class__.__name__ == "Triebwagen":
                spurweite = waggon.spurweite
                triebwagen = {
                    "fahrgestellnummer": waggon.fg_nummer,
                    "max_zugkraft": waggon.max_zugkraft
                }
            else:
                personenwaggons.append(
                    {
                        "fahrgestellnummer": waggon.fg_nummer,
                        "sitzanzahl": waggon.sitzanzahl,
                        "gewicht": waggon.gewicht,
                        "fahrgestellnummer": waggon.fg_nummer,
                    },
                )

        zuege_list.append(
            {
                "zugnummer": zug.nummer,
                "spurweite": spurweite,
                "triebwagen": triebwagen,
                "personenwaggons": personenwaggons,
            }
        )

    return jsonify(zuege_list)


@api.get("/zuege-komp")
def getZuegeMin():
    zuege = Zug.query.all()
    spurweite = 0
    zuege_list = []
    wartungen_list = []

    for zug in zuege:
        wartungen_list = []
        sitzplaetze = 0
        for waggon in zug.waggons:
            if waggon.__class__.__name__ == "Personenwaggon":
                spurweite = waggon.spurweite
                sitzplaetze += waggon.sitzanzahl

        for wartung in zug.wartungen:
            wartungen_list.append(
                {
                    "datum": wartung.datum.isoformat(),
                    "start": str(wartung.start.strftime("%H:%M")),
                    "ende": str(wartung.ende.strftime("%H:%M")),
                }
            )

        zuege_list.append(
            {
                "zugnummer": zug.nummer,
                "spurweite": spurweite,
                "sitzplaetze": sitzplaetze,
                "wartungen": wartungen_list,
            }
        )

    return jsonify(zuege_list)


@api.get("/zug/<nummer>")
def getZug(nummer):
    triebwagen = {}
    zug_print = {}
    personenwaggons = []
    zug = Zug.query.filter_by(nummer=nummer).first()

    for waggon in zug.waggons:
        if waggon.__class__.__name__ == "Triebwagen":
            zug_print = {
                "zugnummer": zug.nummer,
                "spurweite": waggon.spurweite,
            }
            triebwagen = {
                "max_zugkraft": waggon.max_zugkraft,
                "fahrgestellnummer": waggon.fg_nummer,
            }
        else:
            personenwaggons.append(
                {
                    "fahrgestellnummer": waggon.fg_nummer,
                    "sitzanzahl": waggon.sitzanzahl,
                    "gewicht": waggon.gewicht,
                    "fahrgestellnummer": waggon.fg_nummer,
                },

            )

    return jsonify(zug=zug_print, triebwagen=triebwagen, personenwaggons=personenwaggons)


@api.get("/wartungen")
def getWartungen():
    wartungen = Wartung.query.all()
    wartungen_list = []

    for wartung in wartungen:
        wartungen_list.append(
            {
                "datum": str(wartung.datum),
                "start": str(wartung.start),
                "ende": str(wartung.ende),
                "zug": wartung.zug,
            }
        )

    return jsonify(wartungen_list)


@api.get("/wartungen/<nummer>")
def getWartungenVonZug(nummer):
    zug = Zug.query.filter_by(nummer=nummer).first()
    wartungen = zug.wartungen
    wartungen_list = []

    for wartung in wartungen:
        wartungen_list.append(
            {
                "datum": str(wartung.datum),
                "start": str(wartung.start),
                "ende": str(wartung.ende),
                "zug": wartung.zug,
            }
        )

    return jsonify(wartungen_list)
