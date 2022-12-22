# Gruppe 3 - Ticketsystem

Folgend wird erklärt wie das Ticketsystem ausgeführt werden kann. 
"Eingabeaufforderung:" bedeutet das der darauffolgende Text in der Eingabeaufforderung ausgeführt werden soll.
In Prerequisites sind alle Systemvoraussetzungen angeführt, dann kann mit der Installation begonnen werden. 
Nach der Installation kann die Applikation gestartet werden, die Funktionen sind kurz erklärt. 

## Prerequisites

### 1. Python
Python kann unter https://www.python.org/downloads/ gedownloaded werden. 
Eingabeaufforderung: pyhton3

### 2. Flask
Die Installation von Flask wird hier https://flask.palletsprojects.com/en/2.2.x/installation/ erklärt.
Eingabeaufforderung: pip install Flask

## Installation

### 1. Clone Repository
Das GitHub Repository https://github.com/andreawieser/prdkegruppe3.git muss gecloned werden, wie das funktioniert ist hier https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository für alle Betriebssysteme erklärt. 
Bitte in das Verzeichnis "tickets" wechseln!

### 2. Virtual environment
Um die virtuelle Umgebung zu erstellen muss der folgende Befehl ausgeführt werden.
Eingabeaufforderung: python3 -m venv .venv
Um die virtuelle Umgebung zu aktivieren muss je nach Betriebssystem einer der folgenden Befehle ausgeführt werden.
Linux - Eingabeaufforderung: source .venv/bin/activate
Windows - Eingabeaufforderung: venv\Scripts\activate

### 3. Packages 
Bitte alle externen Pakete installieren!
Eingabeaufforderung: pip install -r requirements.txt

### 4. Database 
Damit User angelegt werden können, musss eine Datenbank erstellt werden. 
Ein Admin muss händisch zur Datenbank hinzugefügt werden, alle Benutzerinnen und Benutzer können sich später registrieren.
Ich habe für den Admin die folgenden Zugangsdaten vorgesehen:  
  Benutzername: admin  
  Passwort: 12345  
Bitte die folgenden Befehle nacheindander ausführen, es können aber auch andere Zugangsdaten gesetzt werden.   
Eingabeaufforderung: flask db init  
Eingabeaufforderung: flask db migrate -m "database creation"  
Eingabeaufforderung: flask db upgrade  
Eingabeaufforderung: pyhton3  
Eingabeaufforderung: from app import db  
Eingabeaufforderung: from app.models import User  
Eingabeaufforderung: u = User(username='admin', email='admin@tickets.com')  
Eingabeaufforderung: u.set_password('12345')  
Eingabeaufforderung: u.set_access('admin')  
Eingabeaufforderung: db.session.add(u)  
Eingabeaufforderung: db.session.commit()  

### 5. Dummydata
In der Klasse api.py muss die Variable "dummydata" auf True gesetzt werden, um die Dummydaten nutzen zu können. 
Wird die Variable auf False gesetzt, werden die Daten der anderen Systeme genutzt. 

## Applikation

### 1. Start
Um die Applikation zu starten muss im Browser diese Adresse http://localhost:5000/ aufgerufen werden und der folgende Befehl ausgeführt werden. 
Eingabeaufforderung: flask run

### 2. Login
Der Fahrplan kann auch ohne Login abgerufen werden. 
Der Admin kann sich mit den oben gesetzen Benutzerdaten einloggen. 
Eine Benutzerin oder ein Benutzer kann sich registrieren und später einloggen. 
Man kann sich jederzeit ausloggen. 

#### Adminansicht
Ein Admin kann zeitlich begrenzte Aktionen für Fahrtstrecken festlegen können. 
Wird keine bestimmte Fahrtstrecke ausgewählt, wird die Aktion für alle vorhandenen Fahrtstrecken festgelegt. 
Alle Aktionen können in der Übersicht eingesehen und gelöscht werden. 

#### Benutzeransicht
Es gibt drei Menüpunkte:
- Meine Daten: Hier können Benutzerinnen und Benutzer ihre Daten ändern.
- Ticket kaufen: Hier können Fahrtdurchführungen gesucht und Tickets gekauft werden. Die Preise werden bei Aktionen automatisch angepasst. Warnungen werden bei der Ticketsuche ausgegeben. 
- Meine Tickets: Hier können alle Tickets die gekauft, verbraucht oder storniert wurden eingesehen werden. Für aktive Tickets kann ein Sitzplatz reserviert werden. 

### 3. Ende
Um die Applikation zu beenden muss die Tastenkombination Ctrl + C in der Eingabeaufforderung gedrückt werden.
