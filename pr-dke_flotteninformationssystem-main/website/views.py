import random
from flask import render_template, Blueprint, flash, request, url_for, redirect
import datetime
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from website import db
from website.auth import admin_required
from website.models import Triebwagen, Personenwaggon, Waggon, User, Zug

views = Blueprint("views", __name__)


# whenever the url "/" is visited, the "home" function gets triggered
@views.route("/", methods=["GET", "POST"])
# makes sure you can't access the homepage unless the user is logged in
@login_required
def home():
    users = User.query.all()
    waggons = Waggon.query.all()
    zuege = Zug.query.all()
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
        return render_template("home.html", user=current_user, waggons=waggons, users=users, zuege=zuege)
    else:
        return render_template("emp-dashboard.html", user=current_user)


@views.route("/flotten", methods=["GET", "POST"])
@admin_required
@login_required
def flotten():
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
                    first_spurweite = waggon.spurweite
                    if waggon.__class__.__name__ == "Triebwagen":
                        triebwagen_counter += 1
                        # if triebwagen_counter > 1:
                        #     flash("Bitte wähle (genau) einen Triebwagen aus.", category="danger")
                        #     return redirect(url_for("views.flotten"))
                        zug_zugkraft = waggon.max_zugkraft
                    else:
                        if waggon.spurweite != first_spurweite:
                            flash("Die Superweiten der Waggons müssen übereinstimmen", category="danger")
                            return redirect(url_for("views.flotten"))
                        personenwaggon_counter += 1
                        sum_weight += waggon.gewicht

            if not waggons_chosen:
                flash("Bitte wähle (passende) Waggons für den Zug aus.", category="danger")
            # elif triebwagen_counter != 1:
            #     flash("Bitte wähle (genau) einen Triebwagen aus.", category="danger")
            elif sum_weight > zug_zugkraft:
                flash("Die Zugkraft des Triebwagens reicht nicht", category="danger")
            elif personenwaggon_counter < 1:
                flash("Bitte wähle zumindest einen Personenwaggon für den Zug aus.", category="danger")
            else:
                random_zug_number = "Z" + str(random.randint(100000000, 999999999))
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


# TODO: edit Zug


@views.route("/wartungen", methods=["GET", "POST"])
@admin_required
@login_required
def wartungen():
    # if request.method == "POST":
    #     if request.form.get("submit_wartung"):
    #         datum = request.form.get("t_fg_nummer")
    #         start = request.form.get("t_spurweite")
    #         ende = request.form.get("max_zugkraft")
    #         zug = request.form.get("zug")
    #         mitarbeiter = request.form.get("mitarbeiter")
    #         if not datum or not start or not ende or not zug or not mitarbeiter:
    #             flash("Bitte vervollständige die Eingabe.", category="danger")
    #         else:
    #             wartung = Wartung(datum=datum, start=start, ende=ende, zug=zug, mitarbeiter=mitarbeiter)
    #             #db.session.add(wartung)
    #             #db.session.commit()
    #             flash("Wartung erstellt!", category="success")
    #
    # wartungen = Wartung.query.all()

    return render_template("wartungen.html", user=current_user)  # , wartungen=wartungen)


@views.route("/emp-dashboard", methods=["GET", "POST"])
@login_required
def emp_dashboard():
    return render_template("emp-dashboard.html", user=current_user)
