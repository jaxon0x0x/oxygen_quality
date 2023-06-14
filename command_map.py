"-----------------------------------------------------command_map-----------------------------------------------------"
"""
    Moduł stanowiący instrukcję przycisku "Wybierz punkt na mapie" głównego okna. Zawiera klasę CommandMap, która 
kolejno:
- wyświetla mapę z naniesionymi punktami lokalizacji stacji pomiarowych,
- po kliknięciu wybranego punktu na mapie - wyświetla listę stacji pomiarowych z wklejonym id klikniętego punktu,
- po wybraniu id parametru - wyświetla wykres danych oraz ich listę,
- po zamknięciu okienka wykresu, a następnie kliknięciu przysciku analizuj - wyświetla linię trendu oraz prostą analizę 
  danych.

Moduł zawiera następujące elementy:
- Tkinter - moduł do tworzenia interfejsu użytkownika,
- sqlite3 - moduł do łączenia z bazą danych database.db,
- geopy - moduł do geolokalizacji,
- get_stations_data - funkcja pobiera listę wszystkich stacji pomiarowych i zapisuje ją w bazie danych SQL,
- get_sensors_data - funkcja pobiera listę stanowisk pomiarowych wybranej stacji i zapisuje ją w bazie danych SQL,
- get_measurements_data - funkcja pobiera listę pomiarów wybranego parametru i zapisuje ją w bazie danych SQL,
- MeasurementAnalysis - klasa do tworzenia analizy danych, w tym wykresów,
- AnalysisWindow - GUI do okienka analizy danych.
"""

from tkinter import *
import tkinter as tk
import sqlite3
from PIL import Image, ImageTk
from get_stations_data import get_stations_data
from get_sensors_data import get_sensors_data
from get_measurements_data import get_measurements_data
from measurement_analysis import MeasurementAnalysis
from print_analysis import AnalysisWindow

class CommandMap(Toplevel):
    """
        Klasa wyświetla mapę Polski z zaznaczonymi punktami lokalizacji stacji pomiarowych. Po kliknięciu na dany punkt
    odsyła użytkownika do listboxa, gdzie po wybraniu stanowiska pomiarowego umożliwia przeglądanie pomiarów wybranego
    parametru, zarówno w formie wykresu, jak i listy. Pozwala także na prostą analizę danych za pomocą dedykowanego
    przycisku.
    """
    def __init__(self, *args, **kwargs):
        """
        Inicjalizuje instancję klasy CommandLocation.

        Args:
            *args: Pozycyjne argumenty przekazywane do klasy bazowej Tk.
            **kwargs: Nazwane argumenty przekazywane do klasy bazowej Tk.
        """
        super().__init__(*args, **kwargs)
        self.title("AirQualityApp")
        self.geometry('1200x800')

        label_name = tk.Label(self, text="---Stacje pomiarowe na terenie Polski---")
        label_line = tk.Label(self, text="")
        label_name.pack()
        label_line.pack()

        map_image = Image.open("Poland_map.png")
        map_width, map_height = map_image.size
        min_longtitude = 14.15
        max_longtitude = 24.2
        min_latitude = 49
        max_latitude = 54.9

        canvas = tk.Canvas(self, width=map_width, height=map_height)
        canvas.pack()
        map_image_tk = ImageTk.PhotoImage(map_image)
        canvas.create_image(0, 0, anchor=tk.NW, image=map_image_tk)

        get_stations_data()

        self.conn = sqlite3.connect('database.db')
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, gegr_lat, gegr_lon FROM stations')
        stations = cursor.fetchall()

        #  dodanie punktów  i podpisów stacji pomiarowych na mapie:
        for id, latitude, longitude in stations:
            x = int((float(longitude) - min_longtitude) * (map_width / (max_longtitude - min_longtitude)))
            y = int((max_latitude - float(latitude)) * (map_height / (max_latitude - min_latitude)))
            # rysowanie okręgu reprezentującego stację
            circle=canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="red", outline="black", tags=(id))
            canvas.create_text(x, y + 10, text=str(id), font=("Arial", 6))
            canvas.tag_bind(circle, "<Button-1>", self.on_point_click)

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

    def on_point_click(self, event):
        """
            Otwiera okienko z listboxem, w którym wyświetla się lista wszytskich stacji pomiarowych. Nr ID klikniętego
        punktu na mapie wyświetla się automatycznie jako entry w okienku wyboru id stacji pomiarowej.
        """
        tag = event.widget.gettags("current")[0]
        new_window = tk.Toplevel()
        new_window.title("AirQualityApp")
        new_window.geometry('900x750')
        tag_label = tk.Label(new_window, text=f"---Stacja o id: {tag}---")
        tag_label.pack()

        frame = tk.Frame(new_window)
        frame.pack(fill=tk.BOTH, expand=tk.NO)

        self.listbox = tk.Listbox(new_window)
        self.listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        scrollbar = tk.Scrollbar(self.listbox, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        label_staionId = tk.Label(frame, text="PODAJ ID STACJI W CELU WYŚWIETLENIA STANOWISK POMIAROWYCH")
        label_id = tk.Label(frame, text="PODAJ ID STANOWISKA W CELU WYŚWIETLENIA DANYCH POMIAROWYCH")
        label_analysis = tk.Label(frame, text="DOKONAJ ANALIZY DANYCH")

        self.entry_staionId = tk.Entry(frame, bd=5)
        self.entry_staionId.insert(0, tag)
        self.entry_id = tk.Entry(frame, bd=5)

        button_stationId = Button(frame, text="Szukaj", command=self.show_sensors_data)
        button_id = Button(frame, text="Szukaj", command=self.show_measurements_data)
        button_analysis = Button(frame, text="Analiza danych", command=AnalysisWindow)

        label_staionId.grid(row=1, column=0, padx=10)
        label_id.grid(row=2, column=0, padx=10)
        label_analysis.grid(row=3, column=0, padx=10)

        self.entry_staionId.grid(row=1, column=1, padx=10)
        self.entry_id.grid(row=2, column=1, padx=10)

        button_stationId.grid(row=1, column=2, padx=10)
        button_id.grid(row=2, column=2, padx=10)
        button_analysis.grid(row=3, column=1, padx=10)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM stations')
        result = cursor.fetchall()

        for row in result:
            self.listbox.insert(tk.END, row)

        self.mainloop()

if __name__ == '__main__': CommandMap()
