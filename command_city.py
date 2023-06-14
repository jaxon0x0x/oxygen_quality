"----------------------------------------------------command_city----------------------------------------------------"
"""
    Moduł stanowiący instrukcję przycisku "Wyszukaj stacje po nazwie miejscowości" głównego okna. Zawiera klasę 
CommandCity, która kolejno:
- wyświetla okno z listboxem, w którym:
    - po wprowadzeniu nazwy miejsowości - wyświetli listę stacji pomiarowych w tej miejscowości (o ile są dostępne),
    - po wybraniu id stacji - wyświetla listę stanowisk pomiarowych, gdzie każde stanowisko mierzy inny parametr,
    - po wybraniu id parametru - wyświetla wykres danych oraz ich listę,
- po zamknięciu okienka wykresu, a następnie kliknięciu przysciku analizuj - wyświetla linię trendu oraz prostą analizę 
danych.

Moduł zawiera następujące elementy:
- Tkinter - moduł do tworzenia interfejsu użytkownika,
- sqlite3 - moduł do łączenia z bazą danych database.db,
- get_stations_data - funkcja pobiera listę wszystkich stacji pomiarowych i zapisuje ją w bazie danych SQL,
- get_sensors_data - funkcja pobiera listę stanowisk pomiarowych wybranej stacji i zapisuje ją w bazie danych SQL,
- get_measurements_data - funkcja pobiera listę pomiarów wybranego parametru i zapisuje ją w bazie danych SQL,
- MeasurementAnalysis - klasa do tworzenia analizy danych, w tym wykresów,
- AnalysisWindow - GUI do okienka analizy danych.
"""

from tkinter import *
import tkinter as tk
import sqlite3
from get_stations_data import get_stations_data
from get_sensors_data import get_sensors_data
from get_measurements_data import get_measurements_data
from measurement_analysis import MeasurementAnalysis
from print_analysis import AnalysisWindow

class CommandCity(Tk):
    """
        Klasa wyświetla listę wszytskich stacji pomiarowych dostępnych w wybranej miejscowości i finalnie umożliwia
    przeglądanie pomiarów wybranych parametrów, zarówno w formie wykresu, jak i listy. Pozwala także na prostą analizę
    danych za pomocą dedykowanego przycisku.
    """

    def __init__(self, *args, **kwargs):
        """
        Inicjalizuje instancję klasy CommandCity.

        Args:
            *args: Pozycyjne argumenty przekazywane do klasy bazowej Tk.
            **kwargs: Nazwane argumenty przekazywane do klasy bazowej Tk.
        """
        super().__init__(*args, **kwargs)
        self.title("AirQualityApp")
        self.geometry('1200x700')

        label_name = tk.Label(self, text="---Wyszukaj stację po nazwie miejscowości---")
        label_line = tk.Label(self, text="")
        label_name.pack()
        label_line.pack()

        self.frame = Frame(self)
        self.frame.pack(fill=BOTH, expand=NO)

        self.listbox = Listbox(self)
        self.listbox.pack(side=TOP, fill=BOTH, expand=YES)
        scrollbar = Scrollbar(self.listbox, orient=VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.label_city = Label(self.frame, text="PODAJ NAZWĘ MIEJSCOWOŚCI W CELU WYŚWIETLENIA DOSTĘPNYCH STACJI:")
        self.label_staionId = Label(self.frame, text="PODAJ ID STACJI W CELU WYŚWIETLENIA STANOWISK POMIAROWYCH:")
        self.label_id = Label(self.frame, text="PODAJ ID STANOWISKA W CELU WYŚWIETLENIA DANYCH POMIAROWYCH:")
        self.label_analysis = Label(self.frame, text="DOKONAJ ANALIZY DANYCH")

        self.entry_city = Entry(self.frame, bd=5)
        self.entry_staionId = Entry(self.frame, bd=5)
        self.entry_id = Entry(self.frame, bd=5)

        self.button_city = Button(self.frame, text="Szukaj", command=self.show_city)
        self.button_stationId = Button(self.frame, text="Szukaj", command=self.show_sensors_data)
        self.button_id = Button(self.frame, text="Szukaj", command=self.show_measurements_data)
        self.button_analysis = Button(self.frame, text="Analiza danych", command=AnalysisWindow)

        self.label_city.grid(row=0, column=0, padx=10)
        self.label_staionId.grid(row=1, column=0, padx=10)
        self.label_id.grid(row=2, column=0, padx=10)
        self.label_analysis.grid(row=3, column=0, padx=10)

        self.entry_city.grid(row=0, column=1, padx=10)
        self.entry_staionId.grid(row=1, column=1, padx=10)
        self.entry_id.grid(row=2, column=1, padx=10)

        self.button_city.grid(row=0, column=2, padx=10)
        self.button_stationId.grid(row=1, column=2, padx=10)
        self.button_id.grid(row=2, column=2, padx=10)
        self.button_analysis.grid(row=3, column=1, padx=10)

        get_stations_data()

        self.conn = sqlite3.connect('database.db')
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM stations')
        result = cursor.fetchall()

        for row in result:
            self.listbox.insert(tk.END, row)

        self.mainloop()

    def show_measurements_data(self):
        """
            Wyświetla dane pomiarowe dla wybranego stanowiska.

            Pobiera wartość ID stanowiska z pola entry_id, pobiera z bazy danych odpowiednie dane pomiarowe
        i wyświetla je w listboxie. Następnie generuje wykres na podstawie tych danych.
        """

        self.listbox.delete(0, END)

        id = int(self.entry_id.get())
        get_measurements_data(id)

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM measurements')
        result = cursor.fetchall()

        for row in result:
            self.listbox.insert(tk.END, row)

        MeasurementAnalysis().chart()

    def show_sensors_data(self):
        """
            Wyświetla listę stanowisk pomiarowych dla wybranej stacji. Każde stanowisko bada osobny parametr.

            Pobiera wartość ID stacji z pola entry_stationId, pobiera z bazy danych odpowiednie stanowiska pomiarowe
        i wyświetla je w listboxie.
        """
        self.listbox.delete(0, END)

        stationId = int(self.entry_staionId.get())
        get_sensors_data(stationId)

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM sensors')
        result = cursor.fetchall()

        for row in result:
            self.listbox.insert(tk.END, row)

    def show_city(self):
        """
            Wyświetla listę stacji pomiarowych w wybranej miejscowości.

            Pobiera wartość nazwy miejscowości z pola entry_city, pobiera z bazy danych odpowiednie stacje pomiarowe,
            o ile występują i wyświetla je w listboxie.
        """
        self.listbox.delete(0, END)

        city_name = str(self.entry_city.get())

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM stations WHERE city_name = ?', (city_name,))
        result = cursor.fetchall()

        for row in result:
            self.listbox.insert(tk.END, row)

if __name__ == '__main__': CommandCity()