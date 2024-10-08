import mysql.connector
import random


class Player:
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
        else:
            self.location = "Suomi"
            self.points = 0
            self.visa_value = 0
            self.garbage_weight = 0
            self.high_score = 0
            self.save_to_db()

    def save_to_db(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO pelaajantiedot (Nimi, Sijainti, Pisteet, VisaArvo, RepunPaino) VALUES (%s, %s, %s, %s, %s)",
            (self.name, self.location, self.points, self.visa_value, self.garbage_weight)
        )
        self.conn.commit()

    def update_points(self, points):
        self.points += points
        if self.points > self.high_score:
            self.high_score = self.points
        self.update_db()

    def update_db(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE pelaajantiedot SET Pisteet = %s, VisaArvo = %s, RepunPaino = %s WHERE Nimi = %s",
            (self.points, self.visa_value, self.garbage_weight, self.name)
        )
        self.conn.commit()

    def collect_item(self, item):
        self.visa_value += item['Arvo']
        self.points += 10  # Bonus points for collecting an item
        self.update_db()

    def dispose_garbage(self):
        if self.garbage_weight > 0:
            self.garbage_weight = 0
            self.points += 5  # Points for disposing of garbage
            self.update_db()
            return True
        return False

    def get_status(self):
        return {
            "name": self.name,
            "location": self.location,
            "points": self.points,
            "visa_value": self.visa_value,
            "garbage_weight": self.garbage_weight,
            "high_score": self.high_score,
        }

    def travel_to_country(self, country):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM maanlisätiedot WHERE iso_country = %s", (country,))
        result = cursor.fetchone()

        if result:
            distance = random.randint(5, 30)  # Simulated travel distance
            if self.garbage_weight + distance <= 100:  # Max garbage weight
                self.location = country
                self.garbage_weight += distance  # Increase garbage weight
                self.update_db()
                return True
        return False

    def tarkista_saavutettavat_lentokentat(self):
        print("Tarkistetaan saavutettavat lentokentät...")  # Debug print
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM airport")
        lentokentät = cursor.fetchall()

        saavutettavat_maat = []
        for lentokenttä in lentokentät:
            cursor.execute("SELECT * FROM maanlisätiedot WHERE iso_country = %s", (lentokenttä['iso_country'],))
            maa_tieto = cursor.fetchone()

            etäisyys = random.randint(5, 30)
            if etäisyys <= 900 and maa_tieto:
                kierrätyspaikka = maa_tieto.get('kierrätyspaikka', 0)  # Default value 0 if not found
                saavutettavat_maat.append((maa_tieto['iso_country'], maa_tieto['ArvoEsine'], kierrätyspaikka))

        return saavutettavat_maat


def main():
    conn = mysql.connector.connect(
        host='localhost',
        port=3306,
        database='demogame',  # Use 'demogame' database
        user='ava',
        password='ava123',
        autocommit=True
    )

    player_name = input("Syötä pelaajan nimi: ")
    player = Player(player_name, conn)

    while True:
        print(player.get_status())

        action = input("Valitse toiminto (kerää esine, tyhjennä roskat, matkusta): ").lower()

        if action == "kerää esine":
            item_id = random.randint(1, 33)  # Assuming items are ID 1-33
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM esineidenarvo WHERE EsineID = %s", (item_id,))
            item = cursor.fetchone()
            if item:
                player.collect_item(item)
                print(f"Keräsit esineen: {item['Nimi']} (arvo: {item['Arvo']})")

        elif action == "tyhjennä roskat":
            if player.dispose_garbage():
                print("Roska tyhjennetty!")
            else:
                print("Ei roskia tyhjennettäväksi.")

        elif action == "matkusta":
            saavutettavat_maat = player.tarkista_saavutettavat_lentokentat()
            if saavutettavat_maat:
                print("Saatavilla olevat maat:")
                for maa in saavutettavat_maat:
                    print(f"Maa: {maa[0]} (ArvoEsine: {maa[1]}, Kierrätyspaikka: {maa[2]})")

                country = input("Syötä matkustettavan maan ISO-koodi: ")
                if player.travel_to_country(country):
                    print(f"Matkustit maahan: {country}")
                else:
                    print("Matka epäonnistui.")
            else:
                print("Ei saavutettavia maita lentokentiltä.")

        else:
            print("Tuntematon toiminto.")

        if player.visa_value >= 100:
            print("Olet saanut tarpeeksi arvokkaan visan! Pääset Suomeen!")
            break

    conn.close()


if __name__ == "__main__":
    main()
