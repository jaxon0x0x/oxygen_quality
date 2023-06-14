"-----------------------------------------------MODUŁ: get_stations_data-----------------------------------------------"
"""
    Moduł zawierający funkcję get_stations, która ze strony http://api.gios.gov.pl/pjp-api/rest/station/findAll
pobiera listę stacji pomiarowych. Dane są zapisywane w postaci tabeli SQL i przechowywane w bazie danych database.db.
    W przypadku braku łączności lub niedostępności usługi pobrane zostaną dane "historycne".

Moduł zawiera następujące elementy:
- requests - moduł do wykonywania zapytań sieciowych,
- sqlite3 - moduł do łączenia z bazą danych database.db,
- json - moduł do konwersji danych między formatem JSON a obiektami Pythona.
"""
import requests
import sqlite3
import json

def get_stations_data():
    """
        Funkcja pobiera listę wszystkich stacji pomiarowych z serwisu GIOS i zapisuje je do tabeli 'stations'
        w pamięci SQLlite. W przypadku błędu podczas pobierania danych, funkcja pobiera dane z pliku 'stations.json',
        jeśli taki istnieje.

        Args:
            Brak.

        Returns:
            None.

        Raises:
            requests.exceptions.RequestException: W przypadku błędu podczas pobierania danych z serwisu GIOS.

        Example:
            get_stations_data()

        Output:
            LISTA DOSTĘPNYCH STACJI:
            (11, 'Czerniawa', '50.912475', '15.312190', 142, 'Czerniawa', 'Świeradów-Zdrój', 'lubański', 'DOLNOŚLĄSKIE', 'ul. Strażacka 7')
            (16, 'Dzierżoniów, ul. Piłsudskiego', '50.732817', '16.648050', 198, 'Dzierżoniów', 'Dzierżoniów', 'dzierżoniowski', 'DOLNOŚLĄSKIE', 'ul. Piłsudskiego 26')
            ...
        """

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    conn.execute('''DROP TABLE IF EXISTS stations''')

    conn.execute('''CREATE TABLE IF NOT EXISTS stations (
                    id INTEGER NOT NULL PRIMARY KEY,
                    station_name TEXT,
                    gegr_lat TEXT,
                    gegr_lon TEXT,
                    city_id INTEGER,
                    city_name TEXT,
                    commune_name TEXT,
                    district_name TEXT,
                    province_name TEXT,
                    address_street TEXT)''')

    try:
        stations = requests.get('http://api.gios.gov.pl/pjp-api/rest/station/findAll').json()
        with open('stations.json', 'w') as f:
            json.dump(stations, f)

    except requests.exceptions.RequestException:
        print('BŁĄD POBIERANIA. WCZYTUJĘ DANE HISTORYCZNE...')
        with open('stations.json', 'r') as f:
            stations = json.load(f)

    for station in stations:
        city = station['city']
        commune = city['commune']
        conn.execute('''INSERT INTO stations (id, station_name, gegr_lat, gegr_lon, city_id, city_name, commune_name, district_name, province_name, address_street)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (station['id'], station['stationName'], station['gegrLat'], station['gegrLon'], city['id'],
                      city['name'], commune['communeName'], commune['districtName'], commune['provinceName'],
                      station['addressStreet']))

    print(f"LISTA DOSTĘPNYCH STACJI:")
    cursor.execute("SELECT * FROM stations")
    for row in cursor.fetchall():
        print(row)

    conn.commit()
    conn.close()



