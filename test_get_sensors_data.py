"----------------------------------------------test_get_sensors_data--------------------------------------------------"
"""
    Moduł zawierający klasę TestGetSensorsData, która testuje funkcję get_sensors_data, która ze strony 
'http://api.gios.gov.pl/pjp-api/rest/station/sensors/' pobiera listę stanowisk pomiarowych. 

Moduł zawiera następujące elementy:
- unittest - moduł do przeprowadzania testów,
- sqlite3 - moduł do łączenia z bazą danych database.db,
- json - moduł do konwersji danych między formatem JSON a obiektami Pythona,
- os - moduł do wykonywania operacji na plikach,
- get_sensors_data - moduł zawierający funkcję get_sensors_data.
"""

import unittest
import sqlite3
import json
import os
from get_sensors_data import get_sensors_data

class TestGetSensorsData(unittest.TestCase):
    """
            Klasa testuje funkcję pobierającą dane odnośnie stanowisk pomiarowych ze strony internetowej GIOŚ i zapisującą
        je do pliku 'sensors.json'.
    """

    def setUp(self):
        """
            Przygotowuje stan przed wykonaniem testu.

            Tworzy tymczasową bazę danych w pamięci, nawiązuje połączenie i tworzy tabelę 'sensors' z odpowiednimi
        kolumnami.
        """
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sensors (
                        id INTEGER NOT NULL PRIMARY KEY,
                        station_id INTEGER REFERENCES stations(id),
                        param_name TEXT,
                        param_formula TEXT,
                        param_code TEXT,
                        id_param INTEGER)''')

    def tearDown(self):
        """
            Działa po zakończeniu testu. Zamyka połączenie z bazą danych.
        """
        self.conn.close()

    def read_sensors_json(self, file_path):
        """
            Odczytuje dane z pliku JSON.

            Otwiera wskazany plik JSON i odczytuje jego zawartość. Jak argument pobiera ścieżkę pliku .json a zwraca
        dane z tego pliku.
        """
        with open(file_path, 'r') as f:
            return json.load(f)

    def create_test_data(self):
        """
            Tworzy testowe dane stanowisk pomiarowych w formie słowników i zapisuje je do pliku sensors.json.
        """
        sensors = [
            {
                "id": 50,
                "stationId": 11,
                "param": {
                    "paramName": "dwutlenek azotu",
                    "paramFormula": "NO2",
                    "paramCode": "NO2",
                    "idParam": 6
                }
            },
            {
                "id": 52,
                "stationId": 11,
                "param": {
                    "paramName": "ozon",
                    "paramFormula": "O3",
                    "paramCode": "O3",
                    "idParam": 5
                }
            }
        ]

        with open('sensors.json', 'w') as f:
            json.dump(sensors, f)

    def test_get_sensors_data(self):
        """
            Testuje funkcję pobierającą dane ze strony internetowej GIOŚ i zapisującą je do pliku 'sensors.json'.
        W tym celu:
        - Wywołuje funkcję get_sensors_data(11) w celu pobrania danych,
        - Sprawdza, czy plik 'sensors.json' został utworzony.
        - Odczytuje dane z pliku JSON.
        - Wykonuje zapytanie do bazy danych i pobiera dane z tabeli 'sensors'.
        - Porównuje dane z pliku JSON z danymi z bazy danych.
        """
        get_sensors_data(11)

        self.assertTrue(os.path.exists('sensors.json'))

        with open('sensors.json', 'r') as f:
            json_data = json.load(f)

        self.cursor.execute("SELECT * FROM sensors")
        db_data = self.cursor.fetchall()

        for json_sensor, db_sensor in zip(json_data, db_data):
            self.assertEqual(json_sensor['id'], db_sensor[0])
            self.assertEqual(json_sensor['stationId'], db_sensor[1])
            self.assertEqual(json_sensor['param']['paramName'], db_sensor[2])
            self.assertEqual(json_sensor['param']['paramFormula'], db_sensor[3])
            self.assertEqual(json_sensor['param']['paramCode'], db_sensor[4])
            self.assertEqual(json_sensor['param']['idParam'], db_sensor[5])

    def test_sensors_data_to_dict(self):
        """
            Testuje funkcję odczytującą dane z pliku 'sensors.json'.
        W tym celu:
        - Odczytuje dane z pliku 'sensors.json',
        - Sprawdza, czy dane są w postaci listy,
        - Sprawdza, czy lista nie jest pusta,
        - Sprawdza, czy wszystkie elementy listy są słownikami,
        - Sprawdza, czy każdy słownik zawiera klucze 'id', 'stationId' i 'param'.
        """
        data = self.read_sensors_json('sensors.json')
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertTrue(all(isinstance(sensor, dict) for sensor in data))
        self.assertTrue(all('id' in sensor and 'stationId' in sensor and 'param' in sensor for sensor in data))

    def test_create_sensors_table(self):
        """
            Testowanie, czy funkcja poprawnie utworzyła tabelę 'sensors' i czy tabela zawiera właściwe kolumny.
        W tym celu:
        - Tworzy połączenie z bazą danych 'database.db' przy użyciu SQLite,
        - Wykonuje testowaną funkcję get_sensors_data(),
        - Sprawdza, czy tabela 'sensors' została utworzona poprzez zapytanie do SQLite,
        - Sprawdza, czy tabela 'sensors' zawiera właściwe kolumny poprzez zapytanie do SQLite.
        """
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        get_sensors_data(11)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensors'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)

        cursor.execute("PRAGMA table_info(sensors)")
        result = cursor.fetchall()
        expected_result = [
            (0, 'id', 'INTEGER', 1, None, 1),
            (1, 'station_id', 'INTEGER', 0, None, 0),
            (2, 'param_name', 'TEXT', 0, None, 0),
            (3, 'param_formula', 'TEXT', 0, None, 0),
            (4, 'param_code', 'TEXT', 0, None, 0),
            (5, 'id_param', 'INTEGER', 0, None, 0)
        ]
        self.assertEqual(result, expected_result)

        conn.close()


if __name__ == '__main__':
    unittest.main()
