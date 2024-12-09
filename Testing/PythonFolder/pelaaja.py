import mysql.connector
import random
import geopy.distance
from geopy.distance import great_circle as GRC

import json

class Pelaaja:
    def __init__(self, name, conn):
        self.name = name
        self.conn = conn
        self.load_player_data()

    def load_player_data(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pelaajantiedot WHERE Nimi = %s", (self.name,))
        result = cursor.fetchone()

        if result:
            self.location = result['Sijainti']
            self.points = result['Pisteet']
            self.visa_value = result['VisaArvo']
            self.garbage_weight = result['RepunPaino']
            self.high_score = result['EnnätysPisteet']
            self.countries_visited = result['Kohteet']
        else:
            self.location = "Albania"
            self.points = 0
            self.visa_value = 0
            self.garbage_weight = 0
            self.high_score = 0
            self.countries_visited = ''
            self.save_to_db()

    def save_to_db(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO pelaajantiedot (Nimi, Sijainti, Kohteet, Pisteet, VisaArvo, RepunPaino) VALUES (%s, %s, %s, %s, %s, %s)",
            (self.name, self.location, self.countries_visited, self.points, self.visa_value, self.garbage_weight)
        )
        self.conn.commit()

    def update_db(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE pelaajantiedot SET Kohteet = %s, Pisteet = %s, VisaArvo = %s, RepunPaino = %s WHERE Nimi = %s",
            (self.countries_visited, self.points, self.visa_value, self.garbage_weight, self.name)
        )
        self.conn.commit()

    def annatiedot(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT * FROM pelaajantiedot")
        result = cursor.fetchone()

        return result
