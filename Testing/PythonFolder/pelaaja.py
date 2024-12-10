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
            "INSERT INTO pelaajantiedot (Nimi, Sijainti, Kohteet, Pisteet, EnnätysPisteet, VisaArvo, RepunPaino) VALUES (%s, %s, %s, %s, %s, %s)",
            (self.name, self.location, self.countries_visited, self.points, self.high_score, self.visa_value, self.garbage_weight)
        )
        self.conn.commit()

    def update_db(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE pelaajantiedot SET Kohteet = %s, Sijainti = %s, Pisteet = %s, EnnätysPisteet = %s, VisaArvo = %s, RepunPaino = %s WHERE Nimi = %s",
            (self.countries_visited, self.location, self.points, self.high_score, self.visa_value, self.garbage_weight, self.name)
        )
        self.conn.commit()

    def annatiedot(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT * FROM pelaajantiedot")
        result = cursor.fetchone()

        return result

    def tyhjennatiedot(self):
        self.location = "Albania"
        self.points = 0
        self.visa_value = 0
        self.garbage_weight = 0
        self.countries_visited = ''

        self.update_db()

    def paluusuomeen(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT maanlisätiedot.PääsyArvo as Arvo FROM maanlisätiedot WHERE maanlisätiedot.iso_country = 'FI'")
        item = cursor.fetchone()

        if self.visa_value >= item['Arvo'] and self.garbage_weight == 0:
            self.location = "Finland"
            self.points += 250

            if self.high_score < self.points:
                self.high_score = self.points

            self.tyhjennatiedot()

            return True

        return False

    def tyhjennaroskat(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(f"SELECT maanlisätiedot.Kierratyspaikka as kierratyspaikka FROM maanlisätiedot, country WHERE maanlisätiedot.iso_country = country.iso_country AND country.name = '{self.location}'")
        result = cursor.fetchone()

        if result:
            if result['kierratyspaikka'] == 1:
                self.garbage_weight = 0
                self.update_db()

                return {
                    "roskamaara": self.garbage_weight,
                    "status": "Onnistui"
                }

        return {
            "roskamaara": self.garbage_weight,
            "status": "Epaonnistui"
        }


    def travel_to_country(self, country_name):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(f"SELECT maanlisätiedot.iso_country as lisäiso, country.iso_country as countryiso, country.name as country_name, maanlisätiedot.ArvoEsine as ArvoEsine, maanlisätiedot.Roska_KG as Roska FROM maanlisätiedot, country WHERE maanlisätiedot.iso_country = country.iso_country AND country.name = '{country_name}'")
        result = cursor.fetchone()

        if result:
            distance = random.randint(5, 30)
            frequency = 100

            if distance <= frequency:
                self.location = country_name
                self.garbage_weight += result['Roska']
                self.update_db()

                if self.collect_item(result['ArvoEsine']):
                    return {
                        "arvoesine": result['ArvoEsine'],
                        "maanimi": result['country_name'],
                        "status": "Onnistui"
                    }
                else:
                    return {
                        "arvoesine": "Keratty",
                        "maanimi": result['country_name'],
                        "status": "Onnistui"
                    }


            else:
                return {
                    "arvoesine": "Ei",
                    "maanimi": result['country_name'],
                    "status": "Epaonnistui"
                }
        else:
            return {
                "arvoesine": "Ei",
                "maanimi": "Ei",
                "status": "Epaonnistui"
            }

    def collect_item(self, item_id):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM esineidenarvo WHERE EsineID = '{item_id}'")
        item = cursor.fetchone()

        if item:
            countries = self.countries_visited.split()

            if item['MaaNimi'] in countries:
                return False
            else:
                self.visa_value += item['Arvo']
                self.points += 10

                print(item['MaaNimi'])

                if self.countries_visited == '':
                    self.countries_visited = self.countries_visited + item['MaaNimi']
                else:
                    self.countries_visited = self.countries_visited + ' ' + item['MaaNimi']

                print(self.countries_visited)

                self.update_db()

                return True
        else:
            return False
