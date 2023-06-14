"------------------------------------------------test_get_stations_data------------------------------------------------"
"""
    Moduł zawierający klasę TestGetStationsData, która testuje funkcję get_stations_data, która ze strony 
http://api.gios.gov.pl/pjp-api/rest/station/findAll pobiera listę stacji pomiarowych. 
    
Moduł zawiera następujące elementy:
- unittest - moduł do przeprowadzania testów,
- sqlite3 - moduł do łączenia z bazą danych database.db,
- json - moduł do konwersji danych między formatem JSON a obiektami Pythona,
- os - moduł do wykonywania operacji na plikach,
- get_stations_data - moduł zawierający funkcję get_stations_data.
"""
import unittest
import sqlite3
import json
import os
from get_stations_data import get_stations_data

class TestGetStationsData(unittest.TestCase):
    """
        Klasa testuje funkcję pobierającą dane odnośnie stacji pomiarowych ze strony internetowej GIOŚ i zapisującą je
    do pliku 'stations.json'.
    """

    def setUp(self):
        """
            Przygotowuje stan przed wykonaniem testu.

            Tworzy tymczasową bazę danych w pamięci, nawiązuje połączenie i tworzy tabelę 'stations' z odpowiednimi
        kolumnami.
        """
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE stations (
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

    def tearDown(self):
        """
            Działa po zakończeniu testu. Zamyka połączenie z bazą danych.
        """
        self.conn.close()

    def read_stations_json(self, file_path):
        """
            Odczytuje dane z pliku JSON.

            Otwiera wskazany plik JSON i odczytuje jego zawartość. Jak argument pobiera ścieżkę pliku .json a zwraca
        dane z tego pliku.
        """

        with open(file_path, 'r') as f:
            data = json.load(f)
        return data

    def create_test_data(self):
        """
            Tworzy testowe dane stacji pomiarowych w formie słowników i zapisuje je do pliku stations.json.
        """

        stations = [
            {
                "id": 1,
                "stationName": "Station 1",
                "gegrLat": "50.1111",
                "gegrLon": "19.2222",
                "city": {
                    "id": 1,
                    "name": "City 1",
                    "commune": {
                        "communeName": "Commune 1",
                        "districtName": "District 1",
                        "provinceName": "Province 1"
                    }
                },
                "addressStreet": "Address 1"
            },
            {
                "id": 2,
                "stationName": "Station 2",
                "gegrLat": "51.1111",
                "gegrLon": "20.2222",
                "city": {
                    "id": 2,
                    "name": "City 2",
                    "commune": {
                        "communeName": "Commune 2",
                        "districtName": "District 2",
                        "provinceName": "Province 2"
                    }
                },
                "addressStreet": "Address 2"
            }
        ]

        with open('stations.json', 'w') as f:
            json.dump(stations, f)

    def test_get_stations_data(self):
        """
            Testuje funkcję pobierającą dane ze strony internetowej GIOŚ i zapisującą je do pliku 'stations.json'.
        W tym celu:
        - Wywołuje funkcję get_stations_data() w celu pobrania danych,
        - Sprawdza, czy plik 'stations.json' został utworzony.
        - Odczytuje dane z pliku JSON.
        - Wykonuje zapytanie do bazy danych i pobiera dane z tabeli 'stations'.
        - Porównuje dane z pliku JSON z danymi z bazy danych.
        """

        get_stations_data()

        self.assertTrue(os.path.exists('stations.json'))

        with open('stations.json', 'r') as f:
            json_data = json.load(f)

        self.cursor.execute("SELECT * FROM stations")
        db_data = self.cursor.fetchall()

        for json_station, db_station in zip(json_data, db_data):
            self.assertEqual(json_station['id'], db_station[0])
            self.assertEqual(json_station['stationName'], db_station[1])
            self.assertEqual(json_station['gegrLat'], db_station[2])
            self.assertEqual(json_station['gegrLon'], db_station[3])
            self.assertEqual(json_station['city']['id'], db_station[4])
            self.assertEqual(json_station['city']['name'], db_station[5])
            self.assertEqual(json_station['city']['commune']['communeName'], db_station[6])
            self.assertEqual(json_station['city']['commune']['districtName'], db_station[7])
            self.assertEqual(json_station['city']['commune']['provinceName'], db_station[8])
            self.assertEqual(json_station['addressStreet'], db_station[9])

    def test_stations_data_to_dict(self):
        """
            Testuje funkcję odczytującą dane z pliku 'stations.json'.
        W tym celu:
        - Odczytuje dane z pliku 'stations.json',
        - Sprawdza, czy dane są w postaci listy,
        - Sprawdza, czy lista nie jest pusta,
        - Sprawdza, czy wszystkie elementy listy są słownikami,
        - Sprawdza, czy każdy słownik zawiera klucze 'id' i 'stationName'.
        """
        data = self.read_stations_json('stations.json')
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertTrue(all(isinstance(station, dict) for station in data))
        self.assertTrue(all('id' in station and 'stationName' in station for station in data))

    def test_create_stations_table(self):
        """
            Testowanie, czy funkcja poprawnie utworzyła tabelę 'stations' i czy tabela zawiera właściwe kolumny.
        W tym celu:
        - Tworzy połączenie z bazą danych 'database.db' przy użyciu SQLite,
        - Wykonuje testowaną funkcję get_stations_data(),
        - Sprawdza, czy tabela 'stations' została utworzona poprzez zapytanie do SQLite,
        - Sprawdza, czy tabela 'stations' zawiera właściwe kolumny poprzez zapytanie do SQLite.
        """
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        get_stations_data()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stations'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)

        cursor.execute("PRAGMA table_info(stations)")
        result = cursor.fetchall()
        expected_result = [
            (0, 'id', 'INTEGER', 1, None, 1),
            (1, 'station_name', 'TEXT', 0, None, 0),
            (2, 'gegr_lat', 'TEXT', 0, None, 0),
            (3, 'gegr_lon', 'TEXT', 0, None, 0),
            (4, 'city_id', 'INTEGER', 0, None, 0),
            (5, 'city_name', 'TEXT', 0, None, 0),
            (6, 'commune_name', 'TEXT', 0, None, 0),
            (7, 'district_name', 'TEXT', 0, None, 0),
            (8, 'province_name', 'TEXT', 0, None, 0),
            (9, 'address_street', 'TEXT', 0, None, 0)
        ]
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
