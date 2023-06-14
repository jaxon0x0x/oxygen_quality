"-------------------------------------------------measurement_analysis-------------------------------------------------"
"""
    Moduł stanowiący analizę danych. Zawiera klasę MeasurementAnalysis, która generuje wykres zawierający pomiary 
wybranego parametru, a także dokonuje prostej analizy danych, w tym pokazuje trend.

Moduł zawiera następujące elementy:
- sqlite3 - moduł do łączenia z bazą danych database.db,
- pandas - moduł, który został wykorzystany do generowania dataframe,
- matplotlib - moduł, który został wykorzystany w celu generowania wykresów
"""

import sqlite3
import pandas as pd
from matplotlib import pyplot as plt

class MeasurementAnalysis():
    """"
    Klasa łączy się z bazą danych i pobiera dane pomiarowe wybranego paramtru. Wykonuje wykresy i analizę danych.
    """
    def __init__(self, db_file='database.db'):
        """
            Inicjalizuje instancję klasy MeasurementAnalysis.
        """
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def get_data(self):
        """
            Pobiera dane, tworzy i zwraca ramkę danych.
        """
        self.cursor.execute('SELECT * FROM measurements')
        data = self.cursor.fetchall()
        df = pd.DataFrame(data)
        df[0] = pd.to_datetime(df[0])
        df[1] = pd.to_numeric(df[1])
        return df

    def chart(self):
        """
            Tworzy wykres.
        """
        df = self.get_data()
        plt.figure(num='Wykres danych', figsize=(14, 7))
        plt.grid(True, which='both')
        plt.title('Wyniki pomiarów')
        plt.xlabel('Data pomiaru [miesiąc-dzień godzina]')
        plt.xticks(rotation=90)
        plt.ylabel('Wartości pomiarowe')
        plt.plot(df[0], df[1], label='Dane')
        plt.legend()
        plt.subplots_adjust(bottom=0.2)
        plt.show()

    def analyze(self):
        """
            Dokonuje prostej analizy danych i rysuje linię trendu metodą średniej kroczącej.
        """
        df = self.get_data()
        plt.figure(num="Analiza danych",figsize=(14, 7))
        plt.grid(True, which='both')
        plt.title('Wyznaczanie linii trendu metodą średniej kroczącej')
        plt.xlabel('Data pomiaru [miesiąc-dzień godzina]')
        plt.xticks(rotation=90)
        plt.ylabel('Wartości pomiarowe')
        max_value = df[1].max()
        min_value = df[1].min()
        min_date = df.loc[df[1].idxmin(), 0]
        max_date = df.loc[df[1].idxmax(), 0]
        data_mean = df[1].mean()
        window_size = len(df) // 10
        trend = df[1].rolling(window=window_size, center=True).mean()
        plt.plot(df[0], df[1], label='Dane')
        plt.plot(df[0], trend, label='Trend')
        plt.legend()
        plt.subplots_adjust(bottom=0.2)
        plt.show()
        self.conn.close()

        return {'max_value': max_value,
                'min_value': min_value,
                'min_date': min_date,
                'max_date': max_date,
                'data_mean': data_mean}

if __name__ == '__main__': MeasurementAnalysis()