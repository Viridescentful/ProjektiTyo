import mysql.connector
import random
import geopy.distance
from geopy.distance import great_circle as GRC

class Pelaaja:
    def __init__(self, nimi, conn):
        self.nimi = nimi
        self.conn = conn
        self.lataa_pelaajatiedot()

    def lataa_pelaajatiedot(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pelaajantiedot WHERE Nimi = %s", (self.nimi,))
        tulos = cursor.fetchone()

        if tulos:
            self.sijainti = tulos['Sijainti']
            self.kohteet = tulos['Kohteet']
            self.pisteet = tulos['Pisteet']
            self.visa_arvo = tulos['VisaArvo']
            self.roskan_paino = tulos['RepunPaino']
            self.ennätys = tulos['EnnätysPisteet']
        else:
            self.sijainti = "Albania"
            self.kohteet = ""
            self.pisteet = 0
            self.visa_arvo = 0
            self.roskan_paino = 0
            self.ennätys = 0
            self.tallenna_db()

    def tallenna_db(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO pelaajantiedot (Nimi, Sijainti, Kohteet, Pisteet, VisaArvo, RepunPaino) VALUES (%s, %s, %s, %s, %s)",
            (self.nimi, self.sijainti, self.kohteet, self.pisteet, self.visa_arvo, self.roskan_paino)
        )
        self.conn.commit()

    def tarkista_saavutettavat_lentokentat(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM airport")
        lentokentät = cursor.fetchall()

        saavutettavat_maat = []
        for lentokenttä in lentokentät:
            cursor.execute("SELECT * FROM maanlisätiedot WHERE iso_country = %s", (lentokenttä['iso_country'],))
            maa_tieto = cursor.fetchone()

            etäisyys = random.randint(5, 30)
            if etäisyys <= 900 and maa_tieto:
                kierrätyspaikka = maa_tieto.get('kierrätyspaikka', 0)  # Oletusarvo 0, jos ei löydy
                saavutettavat_maat.append((maa_tieto['iso_country'], maa_tieto['ArvoEsine'], kierrätyspaikka))

        return saavutettavat_maat

    def matkusta_maahan(self, maa):
        saavutettavat_maat = self.tarkista_saavutettavat_lentokentat()

        if any(m[0] == maa for m in saavutettavat_maat):
            self.sijainti = maa
            self.päivitys_db()
            print(f"Matkustit maahan: {maa}")
            for m in saavutettavat_maat:
                if m[0] == maa:
                    print(f"Maa: {m[0]}, Tarvittava arvo: {m[1]}, Kierrätyspaikka: {m[2]}")
            return True
        else:
            print("Matka epäonnistui tai maa ei ole saatavilla.")
            return False

    def get_status(self):
        return {
            "nimi": self.nimi,
            "sijainti": self.sijainti,
            "pisteet": self.pisteet,
            "visa_arvo": self.visa_arvo,
            "roskan_paino": self.roskan_paino,
            "ennätys": self.ennätys,
        }

    def kerää_esine(self, esine):
        self.visa_arvo += esine['Arvo']
        self.pisteet += 10
        self.päivitys_db()

    def tyhjennä_roskat(self):
        if self.roskan_paino > 0:
            self.roskan_paino = 0
            self.pisteet += 5
            self.päivitys_db()
            return True
        return False

    def päivitys_db(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE pelaajantiedot SET Pisteet = %s, VisaArvo = %s, RepunPaino = %s, Kohteet = %s WHERE Nimi = %s",
            (self.pisteet, self.visa_arvo, self.roskan_paino, self.kohteet, self.nimi)
        )
        self.conn.commit()


def pääohjelma():
    conn = mysql.connector.connect(
        host='localhost',
        port=3306,
        database='flight_game',
        user='Veikko',
        password='SQLTemp',
        autocommit=True
    )

    pelaajan_nimi = input("Syötä pelaajan nimi: ")
    pelaaja = Pelaaja(pelaajan_nimi, conn)

    while True:
        print("\nPelaajan tiedot:", pelaaja.get_status())

        toiminto = input("Valitse toiminto (kerää esine, tyhjennä roskat, matkusta): ").lower()

        if toiminto == "kerää esine":
            esine_id = random.randint(1, 33)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM esineidenarvo WHERE EsineID = %s", (esine_id,))
            esine = cursor.fetchone()
            if esine:
                pelaaja.kerää_esine(esine)

        elif toiminto == "tyhjennä roskat":
            pelaaja.tyhjennä_roskat()

        elif toiminto == "matkusta":
            saavutettavat_maat = pelaaja.tarkista_saavutettavat_lentokentat()
            print("Saatavilla olevat maat:")
            for m in saavutettavat_maat:
                print(f"Maa: {m[0]}, Tarvittava arvo: {m[1]}, Kierrätyspaikka: {m[2]}")
            maa = input("Syötä matkustettavan maan ISO-koodi: ")
            pelaaja.matkusta_maahan(maa)

        else:
            print("Tuntematon toiminto.")

        if pelaaja.visa_arvo >= 100:
            print("Olet saanut tarpeeksi arvokkaan visan! Pääset Suomeen!")
            break

    conn.close()

if __name__ == "__main__":
    pääohjelma()