"---------------------------------------------MODUŁ: get_measurements_data---------------------------------------------"
"""
    Moduł zawierający funkcję get_measurements, która ze strony https://api.gios.gov.pl/pjp-api/rest/data/getData/
pobiera listę danych pomiarowych dla wybranego przez użytkownika parametru. Dane są zapisywane w postaci tabeli SQL
i przechowywane w bazie danych database.db.
    W przypadku braku łączności lub niedostępności usługi pobrane zostaną dane "historycne".

Moduł zawiera następujące elementy:
- requests - moduł do wykonywania zapytań sieciowych,
- sqlite3 - moduł do łączenia z bazą danych database.db,
- json - moduł do konwersji danych między formatem JSON a obiektami Pythona.
"""

import requests
import sqlite3
import json

def get_measurements_data(id):
    """
        Funkcja pobiera listę danych pomiarowych z serwisu GIOŚ i zapisuje je do tabeli 'measuremennts' w pamięci
        SQLlite. W przypadku błędu podczas pobierania danych, funkcja pobiera dane z pliku 'measurements.json',
        jeśli taki istnieje.

        Args:
            id (int): Numer ID stanowiska pomiarowego.

        Returns:
            None.

        Raises:
            requests.exceptions.RequestException: W przypadku błędu podczas pobierania danych z serwisu GIOS.

        Example:
            get_measurements_data(id)

        Output:
            LISTA DANYCH ZEBRANYCH ZE STANOWISKA NR 50:
            ('2023-03-12 10:00:00', 1.23808)
            ('2023-03-12 09:00:00', 0.77415)
            ...
        """

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    conn.execute('''DROP TABLE IF EXISTS measurements''')

    conn.execute('''CREATE TABLE IF NOT EXISTS measurements (
                    values_date DATETIME NOT NULL,
                    values_value FLOAT)''')

    try:
        measurements = requests.get(('https://api.gios.gov.pl/pjp-api/rest/data/getData/') + str(id)).json()
        with open('measurements.json', 'w') as f:
            json.dump(measurements, f)

    except requests.exceptions.RequestException:
        print('BŁĄD POBIERANIA. WCZYTUJĘ DANE HISTORYCZNE...')
        with open('measurements.json', 'r') as f:
            measurements = json.load(f)

    for measurement in measurements['values']:
        conn.execute('''INSERT INTO measurements (values_date, values_value)
                        VALUES (?, ?)''',
                     (measurement['date'], measurement['value']))

    print(f"LISTA DANYCH ZEBRANYCH ZE STANOWISKA NR {id}:")
    cursor.execute("SELECT * FROM measurements")
    for row in cursor.fetchall():
        print(row)

    conn.commit()
    conn.close()

