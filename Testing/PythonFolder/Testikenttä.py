import mysql.connector
import random
import geopy.distance
from geopy.distance import great_circle as GRC

import json
from flask import Flask, request
from database import Database
from pelaaja import Pelaaja
from flask_cors import CORS

db = Database()
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/aloitapeli/<nimi>')
def aloitapeli(nimi): #127.0.0.1:5000/aloitapeli/Veikko
    uusipelaaja = Pelaaja(nimi, db.conn)

    vastaus = {
        "Pelaajan Nimi": f"{uusipelaaja.name}",
    }

    return vastaus

@app.route('/paivitatiedot/<nimi>')
def paivitysfunktio(nimi): #127.0.0.1:5000/paivitatiedot/Veikko
    uusipelaaja = Pelaaja(nimi, db.conn)

    vastaus = uusipelaaja.annatiedot()

    return vastaus

@app.route('/lento')
def lentofunktio(): #127.0.0.1:5000/lento?name=Veikko&maa=Germany
    args = request.args

    print(args.get("name"), args.get("maa"))

    uusipelaaja = Pelaaja(args.get("name"), db.conn)
    vastaus = uusipelaaja.travel_to_country(args.get("maa"))

    return vastaus

@app.route('/tyhjennaroskat/<nimi>')
def roskafunktio(nimi): #127.0.0.1:5000/tyhjennaroskat/Veikko
    uusipelaaja = Pelaaja(nimi, db.conn)

    vastaus = uusipelaaja.tyhjennaroskat()

    return vastaus

@app.route('/maantiedot/<maa>')
def maantiedotfunktio(maa): #127.0.0.1:5000/maantiedot/Germany
    cursor = db.conn.cursor(dictionary=True)
    cursor.execute(
        f"SELECT maanlisätiedot.Kierratyspaikka as kierratyspaikka, country.iso_country as maaiso, country.name as maanimi, maanlisätiedot.ArvoEsine as arvoesine, maanlisätiedot.Roska_KG as roska, airport.latitude_deg as lat, airport.longitude_deg as lon FROM maanlisätiedot, country, airport WHERE maanlisätiedot.iso_country = country.iso_country AND airport.ident = maanlisätiedot.ICAO AND country.name = '{maa}'")
    result = cursor.fetchone()

    return result

@app.route('/kaikkimaat')
def kaikkimaattfunktio(): #127.0.0.1:5000/kaikkimaat
    cursor = db.conn.cursor(dictionary=True)
    cursor.execute(
        f"SELECT maanlisätiedot.Kierratyspaikka as kierratyspaikka, country.iso_country as maaiso, country.name as maanimi, maanlisätiedot.ArvoEsine as arvoesine, maanlisätiedot.Roska_KG as roska, airport.latitude_deg as lat, airport.longitude_deg as lon FROM maanlisätiedot LEFT JOIN country ON maanlisätiedot.iso_country = country.iso_country LEFT JOIN airport ON airport.ident = maanlisätiedot.ICAO")
    result = cursor.fetchall()

    return result

@app.route('/paluusuomeen/<nimi>')
def lopetusfunktio(nimi): #127.0.0.1:5000/paluusuomeen/Veikko
    uusipelaaja = Pelaaja(nimi, db.conn)
    vastaus = uusipelaaja.paluusuomeen()

    return vastaus

@app.route('/lopetapeli/<nimi>')
def lopetusfunktio(nimi): #127.0.0.1:5000/lopetapeli/Veikko
    uusipelaaja = Pelaaja(nimi, db.conn)
    uusipelaaja.tyhjennatiedot()

    return "Tiedot Tyhjennetty"

if __name__ == '__main__':
    app.run(use_reloader=True, host='127.0.0.1', port=5000)