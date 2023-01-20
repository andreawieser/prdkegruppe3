from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, json
from flask_login import login_required, current_user
from .models import Post, User, Car, Student
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
from . import db

from website import api

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
    # users = api.getUsers()
    plannedRoutes = api.get_strecken()
    zuege = api.get_zuege()

    if request.method == "POST":
        # text = request.form.get('text')
        # start = request.form.get('start')
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
        # anzahl_wochen = request.form.get('anzahl_wochen')
        # select_time_or_intervall = request.form.get('select_time_or_intervall')
        # select_day_or_weekday = request.form.get('select_day_or_weekday')
        checkbox_tag = request.form.get('checkbox1')
        checkbox_uhrzeit = request.form.get('checkbox3')

        # zug = api.get_zug(request.form.get('select_zug'))

        # if not text:
        #     flash('Felder fehlen!', category='error')
        if checkbox_tag and request.form.get('checkbox2'):
            flash('Nur eine Option auswählen! Datum oder Wochentag', category='error')
        if checkbox_uhrzeit and request.form.get('checkbox4'):
            flash('Nur eine Option auswählen! Uhrzeit oder Zeitintervall', category='error')
        if float(preis) < float(api.get_preis_von_fahrtstrecke(strecken)):
            flash('Preis zu niedrig! Muss mindestens ' + str(api.get_preis_von_fahrtstrecke(strecken)) + ' € betragen!', category='error')
        if api.get_spurweite(str(zug),str(strecken)):
            flash('Spurweite passt nicht, wähle einen anderen Zug!', category='error')
        else:
            # if str(select_day_or_weekday) is 'Tag':
            if checkbox_tag:
                date_list = datum.split(",")
                for d in date_list:
                    if checkbox_uhrzeit:
                        time_list = uhrzeit.split(",")
                        for t in time_list:
                            datetime_uhrzeit = datetime.strptime(t, '%H:%M')
                            datetime_dauer = timedelta(hours=api.get_dauer_von_fahrtstrecke(strecken))
                            datetime_ankunft = datetime_uhrzeit + datetime_dauer
                            if api.get_besetzt(zug,t,str(datetime_ankunft.time())[0:5],d):
                                flash('Zug' + zug + ' ist zum ausgewählten Zeitpunkt ' + t + ' Uhr am ' + d + ' nicht verfügbar!', category='error')    
                            else:
                                post = Post(ankunft=str(datetime_ankunft.time())[0:5],start=str(api.get_station((api.get_start(strecken)))), ziel=str(api.get_station(api.get_end(strecken))), zug=zug, bordpersonal=bordpersonal, preis=preis, datum=d, uhrzeit=t, author=current_user.id)
                                db.session.add(post)
                                db.session.commit()
                                flash('Fahrtdurchführung mit dem Zug ' + zug + ' um ' + t + ' Uhr am ' + d + ' wurde erstellt!', category='success')
                    else:
                        datetime_von = datetime.strptime(von, '%H:%M')
                        datetime_bis = datetime.strptime(bis, '%H:%M')
                        datetime_intervall = timedelta(minutes=int(intervall))
                
                        while datetime_von <= datetime_bis:
                            datetime_uhrzeit = datetime_von
                            datetime_dauer = timedelta(hours=api.get_dauer_von_fahrtstrecke(strecken))
                            datetime_ankunft = datetime_uhrzeit + datetime_dauer
                            if api.get_besetzt(zug,str(datetime_von.time())[0:5],str(datetime_ankunft.time())[0:5],d):
                                flash('Zug' + zug + ' ist zum ausgewählten Zeitpunkt ' + str(datetime_von.time())[0:5] + ' Uhr am ' + d + ' nicht verfügbar!', category='error')
                            else:
                                post = Post(ankunft=str(datetime_ankunft.time())[0:5], start=str(api.get_station((api.get_start(strecken)))), ziel=str(api.get_station(api.get_end(strecken))), zug=zug, bordpersonal=bordpersonal, preis=preis, datum=d, uhrzeit=str(datetime_von.time())[0:5], author=current_user.id)
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
                                datetime_dauer = timedelta(hours=api.get_dauer_von_fahrtstrecke(strecken))
                                datetime_ankunft = datetime_uhrzeit + datetime_dauer
                                if api.get_besetzt(zug,t,str(datetime_ankunft.time())[0:5],str(nextDay.strftime("%d.%m.%y"))):
                                    flash('Zug' + zug + ' ist zum ausgewählten Zeitpunkt ' + t + ' Uhr am ' + str(nextDay.strftime("%d.%m.%y")) + ' nicht verfügbar!', category='error')
                                else:
                                    post = Post(ankunft=str(datetime_ankunft.time())[0:5],start=str(api.get_station((api.get_start(strecken)))), ziel=str(api.get_station(api.get_end(strecken))), zug=zug, bordpersonal=bordpersonal, preis=preis, datum=str(nextDay.strftime("%d.%m.%y")), uhrzeit=t, author=current_user.id)
                                    db.session.add(post)
                                    db.session.commit()
                                    flash('Fahrtdurchführung mit dem Zug ' + zug + ' um ' + t + ' Uhr am ' + str(nextDay.strftime("%d.%m.%y")) + ' wurde erstellt!', category='success')
                        else:
                            datetime_von = datetime.strptime(von, '%H:%M')
                            datetime_bis = datetime.strptime(bis, '%H:%M')
                            datetime_intervall = timedelta(minutes=int(intervall))
                
                            while datetime_von <= datetime_bis:
                                datetime_uhrzeit = datetime_von
                                datetime_dauer = timedelta(hours=api.get_dauer_von_fahrtstrecke(strecken))
                                datetime_ankunft = datetime_uhrzeit + datetime_dauer
                                if api.get_besetzt(zug,str(datetime_von.time())[0:5],str(datetime_ankunft.time())[0:5],str(nextDay.strftime("%d.%m.%y"))):
                                    flash('Zug' + zug + ' ist zum ausgewählten Zeitpunkt ' + str(datetime_von.time())[0:5] + ' Uhr am ' + str(nextDay.strftime("%d.%m.%y")) + ' nicht verfügbar!', category='error')
                                else:
                                    post = Post(ankunft=str(datetime_ankunft.time())[0:5], start=str(api.get_station((api.get_start(strecken)))), ziel=str(api.get_station(api.get_end(strecken))), zug=zug, bordpersonal=bordpersonal, preis=preis, datum=str(nextDay.strftime("%d.%m.%y")), uhrzeit=str(datetime_von.time())[0:5], author=current_user.id)
                                    db.session.add(post)
                                    db.session.commit()
                                    flash('Fahrtdurchführung mit dem Zug ' + zug + ' um ' + str(datetime_von.time())[0:5] + ' Uhr am ' + str(nextDay.strftime("%d.%m.%y")) + ' wurde erstellt!', category='success')
                                datetime_von = datetime_von + datetime_intervall
                        i = i + 1
                    

                # post = Post(text=text, start=start, zug=zug, bordpersonal=bordpersonal, ziel=ziel, preis=preis, datum=datum, author=current_user.id)
                # db.session.add(post)
                # db.session.commit()
                flash('Fahrtdurchführung erstellt!', category='success')
                return redirect(url_for('views.home'))

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

    # posts = Post.query.filter_by(author=user.id).all()
    # posts = Post.query.filter_by(user.id in bordpersonal.split(",")).all()
    # posts = Post.query.filter_by(user.id == 1).all()
    # id_list = d.bordpersonal.split(",")
    # posts = Post.query.filter_by(user.id)
    posts = api.get_fahrten_von_bordpersonal(user.id)
    return render_template("posts.html", user=current_user, posts=posts, username=username)

@views.route("/fahrplan")
def getfahrplan():
    fahrten = Post.query.all()
    fahrten_liste = []

    for fahrt in fahrten:
        fahrten_liste.append(
            {
                "id": fahrt.id,
                "startStation": fahrt.start,
                "endStation": fahrt.ziel,
                "train_id": fahrt.zug,
                "price": fahrt.preis,
                "Datum": fahrt.datum,
                "time": fahrt.uhrzeit,
                "Ankunft": fahrt.ankunft,

            }
        )
    return jsonify(fahrten_liste)
    