# Anleitung Fahrplansystem

In dieser Anleitung wird erklärt, welche Schritte nötig sind, um das Fahrplansystem ausführen zu können und wie die Website funktioniert.

## 1.	Coding Environment
Als Entwicklungsumgebung wurde Visual Studio verwendet und die verwendete Programmiersprache ist Python.

## 2.	Flask Setup
Um das Programm nutzen zu können, müssen über die Eingabeaufforderung folgende Installationen erfolgen:
-	pip install flask
-	pip install Flask-SQLAlchemy
-	pip install flask-login

## 3.	Ausführen der Applikation
Um auf das Programm zugreifen zu können, kann das Repositorie entweder geklont werden, oder der Code kann mittels ZIP-Ordner heruntergeladen werden.

## 4.	Dummydaten
Möchte man die Strecken aus den Dummydaten beziehen, muss man im File „methods.py“ im Ordner „website“ die boolean Variable dummydate in Zeile 7 auf True stellen. Möchte man die Daten vom Streckensystem beziehen muss diese Variable auf False gestellt sein. Des Weiteren muss das Streckensystem davor ausgeführt worden sein, damit die Strecken beim starten hereingeladen werden können. 

## 5.	Programm starten
Um das Programm zu starten, muss der File app.py ausgeführt werden. Danach kann man dem Terminal den URL für die Website entnehmen.
Nach dem Aufrufen des URLs befindet man sich auf der Login Seite. Man kann entweder einen neuen Benutzer anlegen, oder loggt sich mit folgenden Admin Account ein:
Email: admin@admin.at
Passwort: adminadmin

Vorerstelltes Bordpersonal Bsp.
Email: bord@personal1.at
Passwort: bordpersonal
(jedes vorerstellte Bordpersonal hat das Passwort "bordpersonal", bei der Email ändert sich lediglich die Nummerierung)

## 6.	Arten von Usern
Es gibt 2 Arten von Usern: Admins und Bordpersonal. Das Bordpersonal hat Zugriff auf alle Fahrtdurchführungen und eine Liste aller Fahrdurchführungen denen sie zugeteilt sind. Admins haben zusätzlich die Möglichkeit neue Fahrdurchführungen zu erstellen, neue Accounts zu erstellen, die Benutzerkonten zu verwalten, sowie Fahrdurchführungen zu bearbeiten und zu löschen.

## 7.	Home
Auf der Registerkarte Home sieht man den Fahrplan. Ist man ein Admin, wird links eine Dropdown Option angezeigt, die einem die Möglichkeit gibt die Fahrtdurchführung zu löschen oder zu bearbeiten. Bearbeitet werden könne der Preis, das Bordpersonal und der Zug. Wählt man den Überbegriff „Bearbeiten“ aus, kann man diese gleichzeitig bearbeiten. Man kann jedoch auch Preis, Bordpersonal und Zug einzeln bearbeiten.

## 8.	Meine Fahrten
In der Registerkarte „Meine Fahrten“ scheinen nur die Fahrten auf, denen der angemeldete User zugeteilt ist.

## 9.	Neue Fahrdurchführung erstellen
Um eine neue Fahrtdurchführung zu erstellen, muss zu allererst eine Strecke gewählt werden. Hier ist es wichtig, nur Strecken zu wählen, welche auch verbunden werden können. Nicht zulässig sind Strecken die einen Kreis bilden. Ist die Strecke nicht möglich bekommt man eine Fehlermeldung.
### Zulässig:
-	Linz-Wien
-	Wien-St.Pölten
### Nicht zulässig:
-	Linz-Wien
-	Wien-Linz
- oder
-	Linz-Wien
-	Salzburg-Klagenfurt

Man kann der Fahrdurchführung Bordpersonal zuteilen. Ist ein zugeteiltes Bordpersonal nicht verfügbar, bekommt man eine Fehlermeldung.
Für die Fahrdurchführung muss man einen Zug auswählen, passt die Spurweite des Zuges nicht auf die ausgewählte Strecke, befindet er sich in der Wartung oder ist er bereits für den Zeitraum einer anderen Fahrdurchführung zugeteilt, bekommt man eine Fehlermeldung. 
Für die Fahrdurchführung muss man einen Preis auswählen. Wählt man für den Preis einen zu geringen Betrag, der die Kosten nicht abdeckt, bekommt man eine Fehlermeldung.

Man muss zwischen Datum oder Wochentag wählen. Wählt man Datum, wird man aufgefordert eine Liste von Daten (getrennt durch einem Beistrich), einzugeben. Dabei ist es wichtig sich an das vorgegebenen Datumsformat zu halten. Wählt man Wochentag, hat man die Möglichkeit alle Wochentage einzugeben, an denen die Fahrtdurchführung stattfinden soll(Ebenfalls getrennt durch einen Beistrich). Des Weiteren kann man angeben für wie viele Wochen diese Fahrtdurchführungen erstellte werden sollen.

Danach muss man zwischen Uhrzeit und Zeitintervall wählen. Es können mehrere Uhrzeiten eingegeben werden (getrennt durch einen Beistrich). Für jedes Datum, wird für jede Uhrzeit eine Fahrtdurchführung erstellt. Beim Zeitintervall wird man aufgefordert den Intervall in Minuten anzugeben, des weiteren den Start und Endzeitpunkt pro Tag. Für jeden Tag/Wochentag werden die Fahrten im Intervall angelegt.

## 10.	Neuen Account erstellen
Um einen neuen Account zu erstellen muss man eine Email Adresse, Username und Passwort festlegen. Des Weiteren muss man festlegen ob der neuen User Admin Rechte besitzt oder nicht.

## 11.	Benutzerkonten verwalten
In der Registerkarte „Benutzerkonten verwalten“ kann ein Admin alle Nutzer einsehen und auch Löschen.

## 12.	Logout 
Über „Logout“ kann man sich wieder abmelden. 
