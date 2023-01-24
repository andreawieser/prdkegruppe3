from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
from . import db

from website import methods

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    users = User.query.all()
    plannedRoutes = methods.get_strecken()
    zuege = methods.get_zuege()

    if request.method == "POST":
        zug = request.form.get('select_zug')
        bordpersonal = ','.join(request.form.getlist("mymultiselect"))
        strecken = ','.join(request.form.getlist("mymultiselect1"))
        preis = request.form.get('preis')
        datum = request.form.get('datum')
        uhrzeit = request.form.get('uhrzeit')
        intervall = request.form.get('zeit_intervall')
        von = request.form.get('von')
        bis = request.form.get('bis')
        wochentag = str(request.form.get('wochen_tag'))
        checkbox_tag = request.form.get('checkbox1')
        checkbox_uhrzeit = request.form.get('checkbox3')

        if not methods.is_kreis(strecken):
            flash('Diese Fahrtstrecke ist nicht möglich! Die Strecken müssen verbindbar sein und dürfen keinen Kreis bilden!', category='error')
            return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)

        if checkbox_tag:
            if request.form.get('checkbox2'):
                flash('Nur eine Option auswählen! Datum oder Wochentag', category='error')
                return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
            if checkbox_uhrzeit:
                if request.form.get('checkbox4'):
                    flash('Nur eine Option auswählen! Uhrzeit oder Zeitintervall', category='error')
                    return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                    
        if float(preis) < float(methods.get_preis_von_fahrtstrecke(strecken)):
            flash('Preis zu niedrig! Muss mindestens ' + str(methods.get_preis_von_fahrtstrecke(strecken)) + ' € betragen!', category='error')
            return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
        if methods.get_spurweite(str(zug),str(strecken)):
            flash('Spurweite passt nicht, wähle einen anderen Zug!', category='error')
            return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)

        if checkbox_tag:
            date_list = datum.split(",")
            for d in date_list:
                if checkbox_uhrzeit:
                    time_list = uhrzeit.split(",")
                    for t in time_list:
                        datetime_uhrzeit = datetime.strptime(t, '%H:%M')
                        datetime_dauer = timedelta(hours=methods.get_dauer_von_fahrtstrecke(strecken))
                        datetime_ankunft = datetime_uhrzeit + datetime_dauer
                        if methods.get_besetzt(zug,t,str(datetime_ankunft.time())[0:5],d):
                            flash('Zug ' + zug + ' ist zum ausgewählten Zeitpunkt ' + t + ' Uhr am ' + d + ' nicht verfügbar!', category='error')  
                            return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                        if methods.get_wartung(zug,t,str(datetime_ankunft.time())[0:5],d):
                            flash('Der Ausgewählter Zug befindet sich zum ausgewählten Zeitpunkt ' + t + ' Uhr am ' + d + ' in der Wartung!', category='error')  
                            return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                        if methods.get_verfügabar_bordpersonal(bordpersonal,t,str(datetime_ankunft.time())[0:5],d):
                            flash('Ausgewähltes Bordpersonal ist zum ausgewählten Zeitpunkt ' + t + ' Uhr am ' + d + ' nicht verfügbar!', category='error')  
                            return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                        else:
                            post = Post(ankunft=str(datetime_ankunft.time())[0:5],start=str(methods.get_station((methods.get_start(strecken)))), ziel=str(methods.get_station(methods.get_end(strecken))), zug=zug, bordpersonal=bordpersonal, preis=preis, datum=d, uhrzeit=t, strecken=strecken, author=current_user.id)
                            db.session.add(post)
                            db.session.commit()
                            flash('Fahrtdurchführung mit dem Zug ' + zug + ' um ' + t + ' Uhr am ' + d + ' wurde erstellt!', category='success')
                else:
                    datetime_von = datetime.strptime(von, '%H:%M')
                    datetime_bis = datetime.strptime(bis, '%H:%M')
                    datetime_intervall = timedelta(minutes=int(intervall))
                
                    while datetime_von <= datetime_bis:
                        datetime_uhrzeit = datetime_von
                        datetime_dauer = timedelta(hours=methods.get_dauer_von_fahrtstrecke(strecken))
                        datetime_ankunft = datetime_uhrzeit + datetime_dauer
                        if methods.get_besetzt(zug,str(datetime_von.time())[0:5],str(datetime_ankunft.time())[0:5],d):
                            flash('Zug ' + zug + ' ist zum ausgewählten Zeitpunkt ' + str(datetime_von.time())[0:5] + ' Uhr am ' + d + ' nicht verfügbar!', category='error')
                            return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                        if methods.get_wartung(zug,str(datetime_von.time())[0:5],str(datetime_ankunft.time())[0:5],d):
                            flash('Der Ausgewählter Zug befindet sich zum ausgewählten Zeitpunkt ' + str(datetime_von.time())[0:5] + ' Uhr am ' + d + ' in der Wartung!', category='error')  
                            return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                        if methods.get_verfügabar_bordpersonal(bordpersonal,str(datetime_von.time())[0:5],str(datetime_ankunft.time())[0:5],d):
                            flash('Ausgewähltes Bordpersonal ist zum ausgewählten Zeitpunkt ' + t + ' Uhr am ' + d + ' nicht verfügbar!', category='error')  
                            return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                        else:
                            post = Post(ankunft=str(datetime_ankunft.time())[0:5], start=str(methods.get_station((methods.get_start(strecken)))), ziel=str(methods.get_station(methods.get_end(strecken))), zug=zug, bordpersonal=bordpersonal, preis=preis, datum=d, uhrzeit=str(datetime_von.time())[0:5], strecken=strecken, author=current_user.id)
                            db.session.add(post)
                            db.session.commit()
                            flash('Fahrtdurchführung mit dem Zug ' + zug + ' um ' + str(datetime_von.time())[0:5] + ' Uhr am ' + d + ' wurde erstellt!', category='success')
                        datetime_von = datetime_von + datetime_intervall
        else:
            date_list = wochentag.split(",")
            final_date_list = []
            for d in date_list:
                i = 1
                anzahl_wochen = int(request.form.get('anzahl_wochen')) + 1
                # nextDay = date.today()
                while i < anzahl_wochen:
                    nextDay = date.today()
                    if str(d) == 'Montag': 
                        nextDay = nextDay + relativedelta(weekday=MO(i))
                    if str(d) == 'Dienstag': 
                        nextDay = nextDay + relativedelta(weekday=TU(i))
                    if str(d) == 'Mittwoch': 
                        nextDay = nextDay + relativedelta(weekday=WE(i))
                    if str(d) == 'Donnerstag': 
                        nextDay = nextDay + relativedelta(weekday=TH(i))
                    if str(d) == 'Freitag': 
                        nextDay = nextDay + relativedelta(weekday=FR(i))
                    if str(d) == 'Samstag': 
                        nextDay = nextDay + relativedelta(weekday=SA(i))
                    if str(d) == 'Sonntag': 
                        nextDay = nextDay + relativedelta(weekday=SU(i))

                    if checkbox_uhrzeit:
                        time_list = uhrzeit.split(",")
                        for t in time_list:
                            datetime_uhrzeit = datetime.strptime(t, '%H:%M')
                            datetime_dauer = timedelta(hours=methods.get_dauer_von_fahrtstrecke(strecken))
                            datetime_ankunft = datetime_uhrzeit + datetime_dauer
                            if methods.get_besetzt(zug,t,str(datetime_ankunft.time())[0:5],str(nextDay.strftime("%d.%m.%y"))):
                                flash('Zug ' + zug + ' ist zum ausgewählten Zeitpunkt ' + t + ' Uhr am ' + str(nextDay.strftime("%d.%m.%y")) + ' nicht verfügbar!', category='error')
                                return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                            if methods.get_wartung(zug,t,str(datetime_ankunft.time())[0:5],str(nextDay.strftime("%d.%m.%y"))):
                                flash('Der Ausgewählter Zug befindet sich zum ausgewählten Zeitpunkt ' + t + ' Uhr am ' + str(nextDay.strftime("%d.%m.%y")) + ' in der Wartung!', category='error')  
                                return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                            if methods.get_verfügabar_bordpersonal(bordpersonal,t,str(datetime_ankunft.time())[0:5],str(nextDay.strftime("%d.%m.%y"))):
                                flash('Ausgewähltes Bordpersonal ist zum ausgewählten Zeitpunkt ' + t + ' Uhr am ' + d + ' nicht verfügbar!', category='error')  
                                return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                            else:
                                post = Post(ankunft=str(datetime_ankunft.time())[0:5],start=str(methods.get_station((methods.get_start(strecken)))), ziel=str(methods.get_station(methods.get_end(strecken))), zug=zug, bordpersonal=bordpersonal, preis=preis, datum=str(nextDay.strftime("%d.%m.%y")), uhrzeit=t, strecken=strecken, author=current_user.id)
                                db.session.add(post)
                                db.session.commit()
                                flash('Fahrtdurchführung mit dem Zug ' + zug + ' um ' + t + ' Uhr am ' + str(nextDay.strftime("%d.%m.%y")) + ' wurde erstellt!', category='success')
                    else:
                        datetime_von = datetime.strptime(von, '%H:%M')
                        datetime_bis = datetime.strptime(bis, '%H:%M')
                        datetime_intervall = timedelta(minutes=int(intervall))
                
                        while datetime_von <= datetime_bis:
                            datetime_uhrzeit = datetime_von
                            datetime_dauer = timedelta(hours=methods.get_dauer_von_fahrtstrecke(strecken))
                            datetime_ankunft = datetime_uhrzeit + datetime_dauer
                            if methods.get_besetzt(zug,str(datetime_von.time())[0:5],str(datetime_ankunft.time())[0:5],str(nextDay.strftime("%d.%m.%y"))):
                                flash('Zug ' + zug + ' ist zum ausgewählten Zeitpunkt ' + str(datetime_von.time())[0:5] + ' Uhr am ' + str(nextDay.strftime("%d.%m.%y")) + ' nicht verfügbar!', category='error')
                                return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                            if methods.get_wartung(zug,str(datetime_von.time())[0:5],str(datetime_ankunft.time())[0:5],str(nextDay.strftime("%d.%m.%y"))):
                                flash('Der Ausgewählter Zug befindet sich zum ausgewählten Zeitpunkt ' + str(datetime_von.time())[0:5] + ' Uhr am ' + str(nextDay.strftime("%d.%m.%y")) + ' in der Wartung!', category='error')  
                                return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                            if methods.get_verfügabar_bordpersonal(bordpersonal,str(datetime_von.time())[0:5],str(datetime_ankunft.time())[0:5],str(nextDay.strftime("%d.%m.%y"))):
                                flash('Ausgewähltes Bordpersonal ist zum ausgewählten Zeitpunkt ' + t + ' Uhr am ' + d + ' nicht verfügbar!', category='error')  
                                return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)
                            else:
                                post = Post(ankunft=str(datetime_ankunft.time())[0:5], start=str(methods.get_station((methods.get_start(strecken)))), ziel=str(methods.get_station(methods.get_end(strecken))), zug=zug, bordpersonal=bordpersonal, preis=preis, datum=str(nextDay.strftime("%d.%m.%y")), uhrzeit=str(datetime_von.time())[0:5], strecken=strecken, author=current_user.id)
                                db.session.add(post)
                                db.session.commit()
                                flash('Fahrtdurchführung mit dem Zug ' + zug + ' um ' + str(datetime_von.time())[0:5] + ' Uhr am ' + str(nextDay.strftime("%d.%m.%y")) + ' wurde erstellt!', category='success')
                            datetime_von = datetime_von + datetime_intervall
                    i = i + 1

    return render_template('create_post.html', user=current_user, users=users, plannedRoutes=plannedRoutes, zuege=zuege)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Fahrtdurchführung existiert nicht.", category='error')
    elif current_user.get_admin() != 'True':
        flash('Du hast nicht die Befugnis diese Fahrtdurchführung zu löschen.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Fahrtdurchführung gelöscht.', category='success')

    return redirect(url_for('views.home'))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('Es existiert kein User mit diesem Usernamen.', category='error')
        return redirect(url_for('views.home'))

    posts = methods.get_fahrten_von_bordpersonal(user.id)
    return render_template("posts.html", user=current_user, posts=posts, username=username)

@views.route("/bearbeiten/<id>", methods=['GET', 'POST'])
@login_required
def bearbeiten(id):
    zuege = methods.get_zuege()
    users = User.query.all()
    bordpersonal_bisher = ''
    preis_bisher = ''
    min_preis = 0
    zug_bisher = ''

    data= Post.query.all()
    for d in data:
        if str(d.id) == str(id):
            bordpersonal_bisher = str(d.bordpersonal)
            preis_bisher = str(d.preis)
            min_preis=str(methods.get_preis_von_fahrtstrecke(d.strecken))
            zug_bisher=str(d.zug)

    if request.method == "POST":
        post = Post.query.filter_by(id=id).first()
        if not post:
            flash("Fahrtdurchführung existiert nicht.", category='error')
        elif current_user.get_admin() != 'True':
            flash('Du hast nicht die Befugnis diese Fahrtdurchführung zu löschen.', category='error')
        else:
            if request.method == "POST":
                bordpersonal = ','.join(request.form.getlist("mymultiselect"))
                preis = request.form.get('preis')
                zug = request.form.get('select_zug')
                data= Post.query.all()

                for d in data:
                    if str(d.id) == str(id):
                        if bordpersonal != '':
                            if d.bordpersonal != bordpersonal:
                                d.bordpersonal = ''
                                db.session.commit()
                                if methods.get_verfügabar_bordpersonal(bordpersonal,d.uhrzeit,d.ankunft,d.datum):
                                    return render_template('bearbeiten.html', user=current_user, id=id, users=users, bordpersonal_bisher=bordpersonal_bisher, preis_bisher=preis_bisher, min_preis=min_preis,zug_bisher=zug_bisher, zuege=zuege)
                            d.bordpersonal = bordpersonal
                        if preis != '':
                            if preis < min_preis:
                                flash('Preis zu niedrig! Muss mindestens ' + min_preis + ' € betragen!', category='error')
                                return render_template('bearbeiten.html', user=current_user, id=id, users=users, bordpersonal_bisher=bordpersonal_bisher, preis_bisher=preis_bisher, min_preis=min_preis,zug_bisher=zug_bisher, zuege=zuege)
                            d.preis = preis
                        if zug != '' and zug != d.zug:
                            if methods.get_besetzt(zug,d.uhrzeit,d.ankunft,d.datum):
                                flash('Ausgewählter Zug ist zum ausgewählten Zeitpunkt ' + d.uhrzeit + ' Uhr am ' + d.datum + ' nicht verfügbar!', category='error')  
                                return render_template('bearbeiten.html', user=current_user, id=id, users=users, bordpersonal_bisher=bordpersonal_bisher, preis_bisher=preis_bisher, min_preis=min_preis,zug_bisher=zug_bisher, zuege=zuege)
                            if methods.get_wartung(zug,d.uhrzeit,d.ankunft,d.datum):
                                flash('Der Ausgewählter Zug befindet sich zum ausgewählten Zeitpunkt ' + d.uhrzeit + ' Uhr am ' + d.datum + ' in der Wartung!', category='error')  
                                return render_template('bearbeiten.html', user=current_user, id=id, users=users, bordpersonal_bisher=bordpersonal_bisher, preis_bisher=preis_bisher, min_preis=min_preis,zug_bisher=zug_bisher, zuege=zuege)
                            if methods.get_spurweite(str(zug),str(d.strecken)):
                                flash('Spurweite passt nicht, wähle einen anderen Zug!', category='error')
                                return render_template('bearbeiten.html', user=current_user, id=id, users=users, bordpersonal_bisher=bordpersonal_bisher, preis_bisher=preis_bisher, min_preis=min_preis,zug_bisher=zug_bisher, zuege=zuege)

                            d.zug = zug
                        db.session.commit()
                        flash('Änderungen gespeichert.', category='success')

    return render_template('bearbeiten.html', user=current_user, id=id, users=users, bordpersonal_bisher=bordpersonal_bisher, preis_bisher=preis_bisher, min_preis=min_preis,zug_bisher=zug_bisher, zuege=zuege)

@views.route("/Accounts", methods=['GET', 'POST'])
@login_required
def get_accounts():
    users = User.query.all()
    return render_template('bordpersonal.html', user=current_user, users=users)

@views.route("/delete-user/<id>")
@login_required
def delete_user(id):
    user = User.query.filter_by(id=id).first()

    if not user:
        flash("User existiert nicht.", category='error')
    elif current_user.get_admin() != 'True':
        flash('Du hast nicht die Befugnis diesen User zu löschen.', category='error')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User wurde gelöscht.', category='success')

    return redirect(url_for('views.home'))


#APIs:

@views.route("/api/fahrplan")
def getfahrplan():
    fahrten = Post.query.all()
    fahrten_liste = []

    for fahrt in fahrten:
        fahrten_liste.append(
            {
                "fahrt_id": fahrt.id,
                "startBhf": fahrt.start,
                "endBhf": fahrt.ziel,
                "Zug": fahrt.zug,
                "Preis": fahrt.preis,
                "Datum": fahrt.datum,
                "Abfahrt": fahrt.uhrzeit,
                "Ankunft": fahrt.ankunft,
                "Strecken_ids": list(map(int, fahrt.strecken.split(","))),
            }
        )
    return jsonify(fahrten_liste)

@views.route("/api/fahrplan/<id>")
def getfahrplan_per_id(id):
    user = User.query.filter_by(id=id).first()

    if not user:
        flash('Es existiert kein User mit diesem Id.', category='error')
        return redirect(url_for('views.home'))

    fahrten = methods.get_fahrten_von_bordpersonal(user.id)
    fahrten_liste = []

    for fahrt in fahrten:
        fahrten_liste.append(
            {
                "fahrt_id": fahrt.id,
                "startBhf": fahrt.start,
                "endBhf": fahrt.ziel,
                "Zug": fahrt.zug,
                "Preis": fahrt.preis,
                "Datum": fahrt.datum,
                "Abfahrt": fahrt.uhrzeit,
                "Ankunft": fahrt.ankunft,
                "Strecken_ids": list(map(int, fahrt.strecken.split(","))),
            }
        )

    return jsonify(fahrten_liste)
    