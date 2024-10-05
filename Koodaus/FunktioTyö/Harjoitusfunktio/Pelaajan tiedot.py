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
            self.countries_visited = set(result['Sijainti'].split(','))
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

    def update_db(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE pelaajantiedot SET Pisteet = %s, VisaArvo = %s, RepunPaino = %s WHERE Nimi = %s",
            (self.points, self.visa_value, self.garbage_weight, self.name)
        )
        self.conn.commit()

    def calculate_flight_frequency(self):
        max_frequency = 100
        frequency = max(0, max_frequency - (self.garbage_weight * 0.5))
        return frequency

    def travel_to_country(self, country_name):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT iso_country, ArvoEsine FROM maanlisätiedot WHERE iso_country = %s",
            (country_name,)
        )
        result = cursor.fetchone()

        if result:
            distance = random.randint(5, 30)
            frequency = self.calculate_flight_frequency()

            if self.garbage_weight + distance <= frequency:
                self.location = country_name
                self.garbage_weight += distance
                self.update_db()
                return result['ArvoEsine']
            else:
                print("Repun paino on liian korkea matkustamiseen.")
        else:
            print("Maa ei löytynyt.")
        return None

    def collect_item(self, item_id):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM esineidenarvo WHERE EsineID = %s", (item_id,))
        item = cursor.fetchone()

        if item:
            self.visa_value += item['Arvo']
            self.points += 10
            self.countries_visited.add(item['MaaNimi'])
            self.update_db()
            return item
        return None

    def dispose_garbage(self):
        if self.garbage_weight > 0:
            self.garbage_weight = 0
            self.points += 5
            self.update_db()
            return True
        return False

    def return_to_finland(self):
        if self.visa_value >= 100 and self.garbage_weight == 0:
            self.location = "Suomi"
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
            "countries_visited": list(self.countries_visited)
        }


def main():
    conn = mysql.connector.connect(
        host='localhost',
        port=3306,
        database='demogame',
        user='ava',
        password='ava123',
        autocommit=True
    )

    player_name = input("Syötä pelaajan nimi: ")
    player = Player(player_name, conn)

    while True:
        action = input("\nValitse toiminto (matkusta, tyhjennä roskat, näytä tiedot, paluu Suomeen, lopeta): ").lower()

        if action == "matkusta":
            country = input("Mihin maan haluat matkustaa? ")
            item_id = player.travel_to_country(country)
            if item_id:
                item = player.collect_item(item_id)
                if item:
                    print(f"Keräsit esineen: {item['Nimi']} (arvo: {item['Arvo']})")
                print(f"Matkustit maahan: {country}")
            else:
                print("Matka epäonnistui tai roskapaino ylittää rajan.")

        elif action == "tyhjennä roskat":
            if player.dispose_garbage():
                print("Roska tyhjennetty!")
            else:
                print("Ei roskia tyhjennettäväksi.")

        elif action == "näytä tiedot":
            status = player.get_status()
            print("\nPelaajan tiedot:")
            print(f"Nimi: {status['name']}")
            print(f"Sijainti: {status['location']}")
            print(f"Pisteet: {status['points']}")
            print(f"Visa-arvo: {status['visa_value']:.2f}")
            print(f"Roskien paino: {status['garbage_weight']:.2f} kg")
            print(f"Ennätys: {status['high_score']}")
            print(f"Vieraillut maat: {', '.join(status['countries_visited'])}")

        elif action == "paluu suomeen":
            if player.return_to_finland():
                print("Olet palannut Suomeen!")
                break
            else:
                print("Sinun on kerättävä tarpeeksi arvoa ja tyhjennettävä roskat ennen paluuta!")

        elif action == "lopeta":
            print("Peli lopetettu.")
            break

        else:
            print("Tuntematon toiminto.")

    conn.close()


if __name__ == "__main__":
    main()