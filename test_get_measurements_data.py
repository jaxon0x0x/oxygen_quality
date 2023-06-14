"----------------------------------------------test_get_measurements_data----------------------------------------------"
"""
    Moduł zawierający klasę TestGetMeasurementsData, która testuje funkcję get_measurements_data, która ze strony 
http://api.gios.gov.pl/pjp-api/rest/data/getData/ pobiera listę danych pomiarowych. 

Moduł zawiera następujące elementy:
- unittest - moduł do przeprowadzania testów,
- sqlite3 - moduł do łączenia z bazą danych database.db,
- json - moduł do konwersji danych między formatem JSON a obiektami Pythona,
- os - moduł do wykonywania operacji na plikach,
- get_measurements_data - moduł zawierający funkcję get_measurements_data.
"""
import unittest
import sqlite3
import json
import os
from get_measurements_data import get_measurements_data

class TestGetMeasurementsData(unittest.TestCase):
    """
            Klasa testuje funkcję pobierającą dane pomiarowe ze strony internetowej GIOŚ i zapisującąje do pliku
        'measurements.json'.
    """

    def setUp(self):
        """
            Przygotowuje stan przed wykonaniem testu.

            Tworzy tymczasową bazę danych w pamięci, nawiązuje połączenie i tworzy tabelę 'measurements' z odpowiednimi
        kolumnami.
        """
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS measurements (
                                values_date DATETIME NOT NULL,
                                values_value FLOAT)''')

    def tearDown(self):
        """
            Działa po zakończeniu testu. Zamyka połączenie z bazą danych.
        """
        self.conn.close()

    def read_measurements_json(self, file_path):
        """
            Odczytuje dane z pliku JSON.

            Otwiera wskazany plik JSON i odczytuje jego zawartość. Jak argument pobiera ścieżkę pliku .json a zwraca
        dane z tego pliku.
        """
        with open(file_path, 'r') as f:
            return json.load(f)

    def create_test_data(self):
        """
            Tworzy testowe dane pomiarowe w formie słowników i zapisuje je do pliku measurements.json.
        """
        measurements = {
            "key": "NO2", "values": [{"date": "2023-05-17 12:00:00", "value": 2.81276},
                                      {"date": "2023-05-17 11:00:00", "value": 3.68007},
                                  ]
                            }

        with open('measurements.json', 'w') as f:
            json.dump(measurements, f)

    def test_get_measurements_data(self):
        """
            Testuje funkcję pobierającą dane ze strony internetowej GIOŚ i zapisującą je do pliku 'measurements.json'.
        W tym celu:
        - Wywołuje funkcję get_measurements_data(50) w celu pobrania danych,
        - Sprawdza, czy plik 'measurements.json' został utworzony.
        - Odczytuje dane z pliku JSON.
        - Wykonuje zapytanie do bazy danych i pobiera dane z tabeli 'measurements'.
        - Porównuje dane z pliku JSON z danymi z bazy danych.
        """

        get_measurements_data(50)

        self.assertTrue(os.path.exists('measurements.json'))

        with open('measurements.json', 'r') as f:
            json_data = json.load(f)

        self.cursor.execute("SELECT * FROM measurements")
        db_data = self.cursor.fetchall()

        for json_measurement, db_measurement in zip(json_data, db_data):
            self.assertEqual(json_measurement['values']['date'], db_measurement[0])
            self.assertEqual(json_measurement['values']['value'], db_measurement[1])
    def test_measurements_data_to_dict(self):
        """
            Testuje funkcję odczytującą dane z pliku 'measurements.json'.
        W tym celu:
        - Odczytuje dane z pliku 'measurements.json',
        - Sprawdza, czy dane są w postaci słownika,
        - Sprawdza, czy słownik nie jest pusty,
        - Sprawdza, czy wszystkie elementy listy są słownikami,
        - Sprawdza, czy każdy słownik zawiera klucze 'date' i 'value'.
        """

        data = self.read_measurements_json('measurements.json')
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data['values']), 0)
        self.assertTrue(all(isinstance(measurement, dict) for measurement in data['values']))
        self.assertTrue(all('date' in measurement and 'value' in measurement for measurement in data['values']))

    def test_create_sensors_table(self):
        """
            Testowanie, czy funkcja poprawnie utworzyła tabelę 'measurements' i czy tabela zawiera właściwe kolumny.
        W tym celu:
        - Tworzy połączenie z bazą danych 'database.db' przy użyciu SQLite,
        - Wykonuje testowaną funkcję get_measurements_data(),
        - Sprawdza, czy tabela 'measurements' została utworzona poprzez zapytanie do SQLite,
        - Sprawdza, czy tabela 'measurements' zawiera właściwe kolumny poprzez zapytanie do SQLite.
        """
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        get_measurements_data(50)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='measurements'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)

        cursor.execute("PRAGMA table_info(measurements)")
        result = cursor.fetchall()
        expected_result = [
            (0, 'values_date', 'DATETIME', 1, None, 0),
            (1, 'values_value', 'FLOAT', 0, None, 0),
        ]
        self.assertEqual(result, expected_result)

        conn.close()


if __name__ == '__main__':
    unittest.main()
