"-----------------------------------------------MODUŁ: get_sensors_data-----------------------------------------------"
"""
    Moduł zawierający funkcję get_sensors, która ze strony https://api.gios.gov.pl/pjp-api/rest/station/sensors/
pobiera listę stanowisk pomiarowych w wybranej przez użytkownika stacji pomiarowej. Dane są zapisywane w postaci tabeli 
SQL i przechowywane w bazie danych database.db.
    W przypadku braku łączności lub niedostępności usługi pobrane zostaną dane "historycne".

Moduł zawiera następujące elementy:
- requests - moduł do wykonywania zapytań sieciowych,
- sqlite3 - moduł do łączenia z bazą danych database.db,
- json - moduł do konwersji danych między formatem JSON a obiektami Pythona.
"""

import requests
import sqlite3
import json

def get_sensors_data(stationId):
    """
        Funkcja pobiera listę stanowisk pomiarowych dla danej stacji pomiarowej z serwisu GIOŚ i zapisuje je do tabeli
        'sensors' w pamięci SQLlite. W przypadku błędu podczas pobierania danych, funkcja pobiera dane z pliku
        'sensors.json', jeśli taki istnieje.

        Args:
            stationId (int): Numer ID stacji pomiarowej.

        Returns:
            None.

        Raises:
            requests.exceptions.RequestException: W przypadku błędu podczas pobierania danych z serwisu GIOS.

        Example:
            get_sensors_data(stationId)

        Output:
            LISTA DOSTĘPNYCH STANOWISK POMIAROWYCH STACJI NR 11:
            (50, 11, 'dwutlenek azotu', 'NO2', 'NO2', 6)
            (52, 11, 'ozon', 'O3', 'O3', 5)
            ...
        """

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    conn.execute('''DROP TABLE IF EXISTS sensors;''')

    conn.execute('''CREATE TABLE IF NOT EXISTS sensors (
                        id INTEGER NOT NULL PRIMARY KEY,
                        station_id INTEGER REFERENCES stations(id),
                        param_name TEXT,
                        param_formula TEXT,
                        param_code TEXT,
                        id_param INTEGER)''')

    try:
        sensors = requests.get(('https://api.gios.gov.pl/pjp-api/rest/station/sensors/') + str(stationId)).json()
        with open('sensors.json', 'w') as f:
            json.dump(sensors, f)

    except requests.exceptions.RequestException:
        print('BŁĄD POBIERANIA. WCZYTUJĘ DANE HISTORYCZNE...')
        with open('sensors.json', 'r') as f:
            sensors = json.load(f)

    for sensor in sensors:
        conn.execute('''INSERT INTO sensors (id, station_id, param_name, param_formula, param_code, id_param)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (sensor['id'], sensor['stationId'], sensor['param']['paramName'], sensor['param']['paramFormula'],
                      sensor['param']['paramCode'], sensor['param']['idParam']))

    print(f'LISTA DOSTĘPNYCH STANOWISK POMIAROWYCH STACJI NR {stationId}:')
    cursor.execute("SELECT * FROM sensors")
    for row in cursor.fetchall():
        print(row)

    conn.commit()
    conn.close()

