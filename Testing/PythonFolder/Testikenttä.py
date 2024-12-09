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
def roskafunktio(nimi):
    uusipelaaja = Pelaaja(nimi, db.conn)

    vastaus = uusipelaaja.annatiedot()

    return vastaus


if __name__ == '__main__':
    app.run(use_reloader=True, host='127.0.0.1', port=5000)