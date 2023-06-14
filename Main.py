"----------------------------------------------------AirQualityApp----------------------------------------------------"
"""
    Aplikacja AirQualityApp pobiera dane dotyczące badań jakości powietrza w Polsce, publikowane bezpłatnie 
przez Główny Inspektorat Ochrony Środowiska (GIOŚ) i zapisuje je w bazie danych. Zapisane dane prezentowane są w formie 
listy oraz wykresu, a następnie dokonywana jest analiza danych.
    Main to główny moduł aplikacji, który służy do jej uruchomienia. Stanowi menu z czterema opcjami nawigacji 
do wyboru, każda opcja podpięta jest do osobnej funkcji. 
    W sytuacji braku braku łączności aplikacja wyświetla dane "historyczne" - poprzednie wyszukiwanie, niezależnie 
od wprowadzanych informacji przez użytkownika.
    
Moduł zawiera następujące elementy:
- Tkinter - moduł do tworzenia interfejsu użytkownika
- CommandFull - klasa obsługująca pełną listę stacji pomiarowych
- CommandCity - klasa obsługująca wyszukiwanie stacji po nazwie miejscowości
- CommandLocation - klasa obsługująca wyszukiwanie najbliżej położonych stacji
- CommandMap - klasa obsługująca wybór punktu na mapie
"""

import tkinter as tk
from command_full import CommandFull
from command_city import CommandCity
from command_location import CommandLocation
from command_map import CommandMap


root = tk.Tk()
root.title("AirQualityApp")
root.geometry('575x300')

label1 = tk.Label(root, text="---Witaj w AirQualityApp!---")
label2 = tk.Label(root, text="---Aplikacji służącej do przeglądania danych pomiarowych---")
label3 = tk.Label(root, text="Wybierz jedną z poniższych opcji, aby rozpocząć...")

label1.pack()
label2.pack()
label3.place(x=25, y=100, width=270, height=30)

button_full = tk.Button(root, text="Pełna lista stacji pomiarowych", command=CommandFull)
button_city = tk.Button(root, text="Wyszukaj stacje po nazwie miejscowości", command=CommandCity)
button_location = tk.Button(root, text="Wyszukaj najbliżej położone stacje", command=CommandLocation)
button_map = tk.Button(root, text="Wybierz punkt na mapie", command=CommandMap)

button_full.place(x=25, y=150, width=250, height=30)
button_city.place(x=300, y=150, width=250, height=30)
button_location.place(x=25, y=200, width=250, height=30)
button_map.place(x=300, y=200, width=250, height=30)

root.mainloop()
