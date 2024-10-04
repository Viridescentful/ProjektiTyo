import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='demogame',
    user='ava',
    password='ava123',
    autocommit=True
)

def parameterize(items):
    return f"""('{"','".join(items)}')"""

maalista = ["Finland", "Denmark"]
maat = parameterize(maalista)

def parameterize(items):
    return f"""('{"','".join(items)}')"""

maalista = [
    "Albania", "Andorra", "Austria", "Belgium", "Bulgaria", "Croatia",
    "Czech Republic", "Denmark", "Estonia", "France", "Germany",
    "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein",
    "Lithuania", "Luxembourg", "Malta", "Netherlands", "Norway",
    "Poland", "Portugal", "Romania", "Slovakia", "Slovenia",
    "Spain", "Sweden", "Switzerland", "Vatican City", "United Kingdom"]
maat = parameterize(maalista)

def get_airports():
    sql = f"""
         WITH RankedAirports AS (
            SELECT country.name AS country_name, airport.name AS airport_name, airport.type,
                   ROW_NUMBER() OVER (PARTITION BY country.name ORDER BY RAND()) AS rn
            FROM airport
            JOIN country ON airport.iso_country = country.iso_country
            WHERE airport.continent = 'EU' 
            AND airport.type = 'large_airport' 
            AND country.name IN {maat}
        )
        SELECT airport_name
        FROM RankedAirports
        WHERE rn = 1;
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()

    for row in result:
        print(row['airport_name'])
    return result

get_airports()