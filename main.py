"""
Hauptanwendung für Auftragsverwaltung
"""
import tkinter as tk
from adapter.manager import DatenManager
from view.hauptfenster import Hauptfenster


def main():
    """Startet die Anwendung"""
    # Datenmanager initialisieren
    manager = DatenManager("config/config.json")
    
    # GUI erstellen
    root = tk.Tk()
    app = Hauptfenster(root, manager)
    
    # Hauptschleife starten
    root.mainloop()


if __name__ == "__main__":
    main()


