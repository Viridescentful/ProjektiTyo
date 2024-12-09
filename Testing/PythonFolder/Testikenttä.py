import mysql.connector
import random
import geopy.distance
from geopy.distance import great_circle as GRC

import json
from flask import Flask
from database import Database
from pelaaja import Pelaaja
from flask_cors import CORS

db = Database()
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/aloitapeli/<nimi>')
def aloitapeli(nimi): #127.0.0.1:5000/aloitapeli
    uusipelaaja = Pelaaja(nimi, db.conn)

    vastaus = {
        "Pelaajan Nimi": f"{uusipelaaja.name}",
    }

    return vastaus

@app.route('/paivitatiedot/<nimi>')
def paivitysfunktio(nimi):
    uusipelaaja = Pelaaja(nimi, db.conn)

    vastaus = uusipelaaja.annatiedot()

    return vastaus

@app.route('/lento/<nimi>')
def lentofunktio(nimi):
    uusipelaaja = Pelaaja(nimi, db.conn)

    vastaus = uusipelaaja.annatiedot()

    return vastaus

@app.route('/tyhjennaroskat/<nimi>')
def roskafunktio(nimi):
    uusipelaaja = Pelaaja(nimi, db.conn)

    vastaus = uusipelaaja.annatiedot()

    return vastaus


if __name__ == '__main__':
    app.run(use_reloader=True, host='127.0.0.1', port=5000)