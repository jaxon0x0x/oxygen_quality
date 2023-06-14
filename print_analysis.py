"----------------------------------------------------print_analysis----------------------------------------------------"
"""
    Moduł stanowiący okienko GUI do analizy danych. Zawiera klasę AnalysisWindow, która generuje graficzny interfejs
okna do analizy danych wybranego parametru.

Moduł zawiera następujące elementy:
- Tkinter - moduł do tworzenia interfejsu użytkownika,
- matplotlib - moduł, który został wykorzystany w celu generowania wykresów,
- measurement_analysis - moduł zawierający klasę MeasurementAnalysis, która generuje wykresy i przelicza wartości.
"""
import tkinter as tk
from measurement_analysis import MeasurementAnalysis

class AnalysisWindow(tk.Tk):
    """
        Klasa wyświetla okienko GUI do analizy danych, które jest podpięte do każdej z czterech opcji nawigacji po
    aplikacji.
    """
    def __init__(self):
        """
            Inicjalizuje instancję klasy AnalysisWindow.
        """
        super().__init__()
        self.analysis = MeasurementAnalysis('database.db')
        self.title('Analiza pomiarów')
        self.geometry('300x200')

        max_value_label = tk.Label(self, text='Największa wartość:')
        max_value_label.grid(column=0, row=0)

        self.max_value_entry = tk.Entry(self, width=20)
        self.max_value_entry.grid(column=1, row=0)

        min_value_label = tk.Label(self, text='Najmniejsza wartość:')
        min_value_label.grid(column=0, row=1)

        self.min_value_entry = tk.Entry(self, width=20)
        self.min_value_entry.grid(column=1, row=1)

        min_date_label = tk.Label(self, text='Data dla wartości najmniejszej:')
        min_date_label.grid(column=0, row=2)

        self.min_date_entry = tk.Entry(self, width=20)
        self.min_date_entry.grid(column=1, row=2)

        max_date_label = tk.Label(self, text='Data dla wartości największej:')
        max_date_label.grid(column=0, row=3)

        self.max_date_entry = tk.Entry(self, width=20)
        self.max_date_entry.grid(column=1, row=3)

        data_mean_label = tk.Label(self, text='Średnia:')
        data_mean_label.grid(column=0, row=4)

        self.data_mean_entry = tk.Entry(self, width=20)
        self.data_mean_entry.grid(column=1, row=4)

        analyze_button = tk.Button(self, text='Analizuj', command=self.command_analyze)
        analyze_button.grid(column=0, row=6, columnspan=2)

    def command_analyze(self):
        """
            Pobiera wyniki analizy danych  przeprowadzonych przez metodę analyze z klasy MeasurementsAnalysis (moduł
        measurement_analysis) i aktualizuje wartości w Entry, wpisując te wyniki.

        Wartości aktualizowane w Entry:
        - max_value_entry: maksymalna wartość,
        - min_value_entry: minimalna wartość,
        - min_date_entry: data odpowiadająca minimalnej wartości,
        - max_date_entry: data odpowiadająca maksymalnej wartości,
        - data_mean_entry: średnia wartość danych.
        """
        analysis_results = self.analysis.analyze()

        self.max_value_entry.delete(0, tk.END)
        self.max_value_entry.insert(0, str(analysis_results['max_value']))

        self.min_value_entry.delete(0, tk.END)
        self.min_value_entry.insert(0, str(analysis_results['min_value']))

        self.min_date_entry.delete(0, tk.END)
        self.min_date_entry.insert(0, str(analysis_results['min_date']))

        self.max_date_entry.delete(0, tk.END)
        self.max_date_entry.insert(0, str(analysis_results['max_date']))

        self.data_mean_entry.delete(0, tk.END)
        self.data_mean_entry.insert(0, str(analysis_results['data_mean']))

if __name__ == '__main__':
    app = AnalysisWindow()
    app.mainloop()

