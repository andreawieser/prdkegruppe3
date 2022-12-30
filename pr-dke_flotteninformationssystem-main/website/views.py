import random
from flask import render_template, Blueprint, flash, request, url_for, redirect
import datetime
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from website import db
from website.auth import admin_required
from website.models import Triebwagen, Personenwaggon, Waggon, User, Zug, Wartung

views = Blueprint("views", __name__)


# whenever the url "/" is visited, the "home" function gets triggered
@views.route("/home", methods=["GET", "POST"])
# makes sure you can't access the homepage unless the user is logged in
@login_required
def home():
    users = User.query.all()
    waggons = Waggon.query.all()
    zuege = Zug.query.all()
    wartungen_home = Wartung.query.order_by(Wartung.datum).all()
    # with current_user I have access to the database like that e.g.: "current_user.id"
    if current_user.is_admin:
        if request.method == "POST":
            if request.form.get("submit_mitarbeiter"):
                email = request.form.get("email")
                password = request.form.get("passwort")
                if not email or not password:
                    flash("Bitte vervollständige die Eingabe.", category="danger")
                else:
                    new_user = User(email=email, password=generate_password_hash(password, method="sha256"))
                    db.session.add(new_user)
                    db.session.commit()
                    flash("Mitarbeiter erstellt!", category="success")
        return render_template("home.html", user=current_user, waggons=waggons, users=users, zuege=zuege,
                               wartungen=wartungen_home)
    else:
        return render_template("emp-dashboard.html", user=current_user, zuege=zuege, waggons=waggons,
                               wartungen=wartungen_home)


@views.route("/flotten", methods=["GET", "POST"])
@admin_required
@login_required
def flotten():
    zug_gattungen = ["RJ ", "WB ", "S ", "NJ ", "ICE ", "IC ", "RJX "]
    if request.method == "POST":
        if request.form.get("submit_twagen"):
            t_fg_nummer = "T" + str(random.randint(100000000, 999999999))
            spurweite = request.form.get("t_spurweite")
            max_zugkraft = request.form.get("max_zugkraft")
            if not spurweite or not max_zugkraft:
                flash("Bitte vervollständige die Eingabe.", category="danger")
            else:
                triebwagen = Triebwagen(fg_nummer=t_fg_nummer, spurweite=spurweite, max_zugkraft=max_zugkraft)
                db.session.add(triebwagen)
                db.session.commit()
                flash("Triebwagen erstellt!", category="success")

        if request.form.get("submit_pwagen"):
            p_fg_nummer = "P" + str(random.randint(100000000, 999999999))
            spurweite = request.form.get("p_spurweite")
            sitzanzahl = request.form.get("sitzanzahl")
            gewicht = request.form.get("gewicht")
            if not spurweite or not sitzanzahl or not gewicht:
                flash("Bitte vervollständige die Eingabe.", category="danger")
            else:
                personenwaggon = Personenwaggon(fg_nummer=p_fg_nummer, spurweite=spurweite,
                                                sitzanzahl=sitzanzahl, gewicht=gewicht)
                db.session.add(personenwaggon)
                db.session.commit()
                flash("Personenwaggon erstellt!", category="success")

        if request.form.get("submit_zug"):
            waggons_fuer_zug = request.form.getlist("gewaehlt_fuer_zug")
            waggons_chosen = []
            triebwagen_counter = 0
            personenwaggon_counter = 0
            first_spurweite = 0
            sum_weight = 0
            zug_zugkraft = 0

            for waggon_id in waggons_fuer_zug:
                waggon = Waggon.query.get(waggon_id)
                if not waggon.in_verwendung:
                    waggons_chosen.append(waggon)
                    if len(waggons_chosen) == 1:
                        first_spurweite = waggon.spurweite
                    if waggon.spurweite != first_spurweite:
                        flash("Die Superweiten der Waggons müssen übereinstimmen", category="danger")
                        return redirect(url_for("views.flotten"))
                    if waggon.__class__.__name__ == "Triebwagen":
                        triebwagen_counter += 1
                        zug_zugkraft = waggon.max_zugkraft
                    else:
                        personenwaggon_counter += 1
                        sum_weight += waggon.gewicht

            if not waggons_chosen:
                flash("Bitte wähle (passende) Waggons für den Zug aus.", category="danger")
            elif sum_weight > zug_zugkraft:
                flash("Die Zugkraft des Triebwagens reicht nicht", category="danger")
            elif personenwaggon_counter < 1:
                flash("Bitte wähle zumindest einen Personenwaggon für den Zug aus.", category="danger")
            else:
                random_zug_number = random.choice(zug_gattungen) + str(random.randint(1000, 9999))
                zug = Zug(nummer=random_zug_number, waggons=waggons_chosen)
                for waggon in waggons_chosen:
                    waggon.in_verwendung = True
                db.session.add(zug)
                db.session.commit()
                flash("Zug erstellt!", category="success")

    waggons = Waggon.query.all()
    zuege = Zug.query.all()

    return render_template("flotten.html", user=current_user, waggons=waggons, zuege=zuege)


@views.route("/delete-waggon/<id>")
@admin_required
@login_required
def delete_waggon(id):
    waggon = Waggon.query.filter_by(id=id).first()
    if not waggon:
        flash("Waggon existiert nicht!", category="danger")
    else:
        zug = Zug.query.get(waggon.zug)
        if zug is not None:
            if zug.waggons < 3 or waggon.type == Triebwagen and waggon.zug is not None:
                db.session.delete(zug)
                flash("Zug wurde gelöscht, da keine korrekte Kombination aus Waggons mehr vorliegt")
        db.session.delete(waggon)
        db.session.commit()
        flash("Waggon gelöscht.", category="success")
    return redirect(url_for("views.flotten"))


@views.route("/delete-zug/<id>")
@admin_required
@login_required
def delete_zug(id):
    zug = Zug.query.filter_by(id=id).first()
    if not zug:
        flash("Zug existiert nicht!", category="danger")
    else:
        for waggon in zug.waggons:
            waggon.in_verwendung = False
        wartung = Wartung.query.filter_by(zug=zug.id).first()
        print(wartung)
        if wartung is not None:
            print("wartung vorhanden: " + str(wartung))
            db.session.delete(wartung)
        db.session.delete(zug)
        db.session.commit()
        flash("Zug aufgelöst.", category="success")
    return redirect(url_for("views.flotten"))


@views.route("/edit-waggon/<id>", methods=["GET", "POST"])
@admin_required
@login_required
def update_waggon(id):
    waggon_to_edit = Waggon.query.filter_by(id=id).first()
    if request.method == "POST":
        if not waggon_to_edit:
            flash("Waggon existiert nicht!", category="danger")
        elif waggon_to_edit.__class__.__name__ == "Triebwagen":
            waggon_to_edit.fg_nummer = request.form["t_fg_nummer"]
            waggon_to_edit.spurweite = request.form["t_spurweite"]
            waggon_to_edit.max_zugkraft = request.form["t_max_zugkraft"]
            db.session.commit()
            flash("Triebwagen aktualisiert.", category="success")
        else:
            waggon_to_edit.fg_nummer = request.form["p_fg_nummer"]
            waggon_to_edit.spurweite = request.form["p_spurweite"]
            waggon_to_edit.sitzanzahl = request.form["sitzanzahl"]
            waggon_to_edit.gewicht = request.form["gewicht"]
            db.session.commit()
            flash("Personenwaggon aktualisiert.", category="success")

        return redirect(url_for("views.flotten"))
    else:
        return render_template("waggon-edit.html", user=current_user, waggon_to_edit=waggon_to_edit)


@views.route("/edit-zug/<id>", methods=["GET", "POST"])
@admin_required
@login_required
def update_zug(id):
    zug_to_edit = Zug.query.filter_by(id=id).first()
    waggons = Waggon.query.all()
    print("Waggons des Zuges vorher: " + str(zug_to_edit.waggons))
    if request.method == "POST":
        if request.form.get("submit_remove"):
            if not zug_to_edit:
                flash("Zug existiert nicht!", category="danger")
            else:
                selected_waggons = request.form.getlist("p_waggons_select")
                if not selected_waggons:
                    flash("Sie haben keine Waggons ausgewählt!", category="danger")
                    return render_template("zug-edit.html", user=current_user, zug_to_edit=zug_to_edit, waggons=waggons)
                print(request.form.getlist("p_waggons_select"))
                for waggon_id in selected_waggons:
                    waggon = Waggon.query.filter_by(id=waggon_id).first()
                    zug_to_edit.waggons.remove(waggon)
                    waggon.in_verwendung = False
                print("Waggons des Zuges nachher: " + str(zug_to_edit.waggons))
                db.session.commit()
                flash("Personenwaggon(s) von Zug entfernt.", category="success")
        else:
            waggons_fuer_zug = request.form.getlist("gewaehlt_fuer_zug")
            sum_weight = 0
            zug_zugkraft = 0

            for waggon in zug_to_edit.waggons:
                if waggon.__class__.__name__ == "Triebwagen":
                    zug_zugkraft = waggon.max_zugkraft
                else:
                    sum_weight += waggon.gewicht

            for waggon_id in waggons_fuer_zug:
                waggon = Waggon.query.get(waggon_id)
                if sum_weight + waggon.gewicht > zug_zugkraft:
                    flash("Die Zugkraft des Triebwagens reicht nicht", category="danger")
                    return render_template("zug-edit.html", user=current_user, zug_to_edit=zug_to_edit, waggons=waggons)
                else:
                    print("Waggon hinzugefügt!")
                    zug_to_edit.waggons.append(waggon)
            db.session.commit()
            flash("Personenwaggon(s) Zug angefügt.", category="success")
            print("Waggons des Zuges nachher: " + str(zug_to_edit.waggons))

        return redirect(url_for("views.flotten"))

    else:
        return render_template("zug-edit.html", user=current_user, zug_to_edit=zug_to_edit, waggons=waggons)


@views.route("/wartungen", methods=["GET", "POST"])
@admin_required
@login_required
def wartungen():
    wartungen_wartung = Wartung.query.order_by(Wartung.datum).all()
    if request.method == "POST":
        if request.form.get("submit_wartung"):
            datum_pre = request.form.get("wartung_datum")
            datum = datetime.date(int(datum_pre[0:4]), int(datum_pre[5:7]), int(datum_pre[8:]))  # jjjj-mm-tt
            start = datetime.time(int(request.form.get("wartung_start")[0:2]),
                                  int(request.form.get("wartung_start")[3:5]))  # hh:mm
            ende = datetime.time(int(request.form.get("wartung_ende")[0:2]),
                                 int(request.form.get("wartung_ende")[3:5]))  # hh:mm
            if ende < start:
                flash("Endzeit ist vor Anfangszeit, bitte ändern", category="danger")
                return redirect(url_for("views.wartungen"))
            zug = Zug.query.filter_by(nummer=request.form.get("wartung_zug")).first()  # Zugnummer (z.B. Z790269576)
            mitarbeiter = User.query.filter_by(email=request.form.get("wartung_mitarbeiter")).first()  # emp@zug.at

            if not datum or not start or not ende or not zug or not mitarbeiter:
                flash("Bitte vervollständige die Eingabe.", category="danger")

            for wartung in wartungen_wartung:
                if wartung.datum == datum and mitarbeiter.id == wartung.mitarbeiter:
                    if start < wartung.ende and ende > wartung.start:
                        flash("Zu dieser Zeit ist der Mitarbeiter bereits zu einer Wartung eingeteilt.",
                              category="danger")
                        return redirect(url_for("views.wartungen"))
            else:
                wartung = Wartung(datum=datum, start=start, ende=ende, zug=zug.id, mitarbeiter=mitarbeiter.id)
                db.session.add(wartung)
                db.session.commit()
                flash("Wartung erstellt!", category="success")
                return redirect(url_for("views.wartungen"))

    zuege = Zug.query.all()
    users = User.query.filter_by(is_admin=False).all()

    return render_template("wartungen.html", user=current_user, wartungen=wartungen_wartung, users=users, zuege=zuege)


@views.route("/delete-wartung/<id>")
@admin_required
@login_required
def delete_wartung(id):
    wartung = Wartung.query.filter_by(id=id).first()
    if not wartung:
        flash("Wartung existiert nicht!", category="danger")
    else:
        db.session.delete(wartung)
        db.session.commit()
        flash("Wartung gelöscht.", category="success")
    return redirect(url_for("views.wartungen"))


@views.route("/edit-wartung/<id>", methods=["GET", "POST"])
@admin_required
@login_required
def update_wartung(id):
    wartung_to_edit = Wartung.query.filter_by(id=id).first()
    if request.method == "POST":
        if not wartung_to_edit:
            flash("Wartung existiert nicht!", category="danger")
        else:
            datum_pre = request.form.get("wartung_datum")
            wartung_to_edit.datum = datetime.date(int(datum_pre[0:4]), int(datum_pre[5:7]),
                                                  int(datum_pre[8:]))  # jjjj-mm-tt
            wartung_to_edit.start = datetime.time(int(request.form.get("wartung_start")[0:2]),
                                                  int(request.form.get("wartung_start")[3:5]))  # hh:mm
            wartung_to_edit.ende = datetime.time(int(request.form.get("wartung_ende")[0:2]),
                                                 int(request.form.get("wartung_ende")[3:5]))  # hh:mm
            if wartung_to_edit.ende < wartung_to_edit.start:
                flash("Endzeit ist vor Anfangszeit, bitte ändern", category="danger")
                return redirect(url_for("views.wartungen"))
            wartung_to_edit.zug = Zug.query.filter_by(
                nummer=request.form.get("wartung_to_edit_zug")).first().id  # Zugnummer (z.B. Z790269576)
            wartung_to_edit.mitarbeiter = User.query.filter_by(
                email=request.form.get("wartung_to_edit_mitarbeiter")).first().id  # emp@zug.at
            db.session.commit()
        flash("Wartung aktualisiert.", category="success")
        return redirect(url_for("views.wartungen"))
    else:
        zuege = Zug.query.all()
        users = User.query.filter_by(is_admin=False).all()
        return render_template("wartung-edit.html", user=current_user, wartung_to_edit=wartung_to_edit, zuege=zuege,
                               users=users)
