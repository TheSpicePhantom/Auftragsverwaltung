"""
Hauptfenster der Anwendung
"""
import tkinter as tk
from tkinter import ttk, messagebox
from adapter.manager import DatenManager


class Hauptfenster:
    """Hauptfenster der Auftragsverwaltung"""
    
    def __init__(self, root: tk.Tk, manager: DatenManager):
        self.root = root
        self.manager = manager
        self.root.title("Auftragsverwaltung - R. W. Kiermeier")
        self.root.geometry("1200x800")
        
        self._erstelle_menue()
        self._erstelle_ui()
    
    def _erstelle_menue(self):
        """Erstellt die Menüleiste"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Datei-Menü
        datei_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datei", menu=datei_menu)
        datei_menu.add_command(label="Einstellungen...", command=self._oeffne_einstellungen)
        datei_menu.add_separator()
        datei_menu.add_command(label="Beenden", command=self.root.quit)
        
        # Daten-Menü
        daten_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Daten", menu=daten_menu)
        daten_menu.add_command(label="Kunden", command=self._oeffne_kunden)
        daten_menu.add_command(label="Aufträge", command=self._oeffne_auftraege)
        daten_menu.add_command(label="Rechnungen", command=self._oeffne_rechnungen)
    
    def _erstelle_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Notebook für Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Übersichts-Tab
        self.uebersicht_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.uebersicht_frame, text="Übersicht")
        self._erstelle_uebersicht()
        
        # Kunden-Tab
        self.kunden_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.kunden_frame, text="Kunden")
        self._erstelle_kunden_ui()
        
        # Aufträge-Tab
        self.auftraege_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.auftraege_frame, text="Aufträge")
        self._erstelle_auftraege_ui()
        
        # Rechnungen-Tab
        self.rechnungen_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rechnungen_frame, text="Rechnungen")
        self._erstelle_rechnungen_ui()
        
        # Speichere Referenz zur RechnungenView für spätere Updates
        self.rechnungen_view = None
    
    def _erstelle_uebersicht(self):
        """Erstellt die Übersichtsseite"""
        # Statistiken
        stats_frame = ttk.LabelFrame(self.uebersicht_frame, text="Statistiken", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        kunden_count = len(self.manager.get_kunden())
        auftraege_count = len(self.manager.get_auftraege())
        rechnungen_count = len(self.manager.get_rechnungen())
        
        ttk.Label(stats_frame, text=f"Kunden: {kunden_count}", font=("Arial", 12)).pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Aufträge: {auftraege_count}", font=("Arial", 12)).pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Rechnungen: {rechnungen_count}", font=("Arial", 12)).pack(anchor=tk.W)
        
        # Offene Rechnungen
        offene_rechnungen = [r for r in self.manager.get_rechnungen() if r.status == "Offen"]
        offener_betrag = sum(r.bruttobetrag for r in offene_rechnungen)
        
        ttk.Label(stats_frame, text=f"Offene Rechnungen: {len(offene_rechnungen)}", font=("Arial", 12)).pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Offener Betrag: {offener_betrag:.2f} €", font=("Arial", 12, "bold")).pack(anchor=tk.W)
    
    def _erstelle_kunden_ui(self):
        """Erstellt die Kunden-UI"""
        from view.kunden_view import KundenView
        KundenView(self.kunden_frame, self.manager)
    
    def _erstelle_auftraege_ui(self):
        """Erstellt die Aufträge-UI"""
        from view.auftraege_view import AuftraegeView
        self.auftraege_view = AuftraegeView(self.auftraege_frame, self.manager, self)
    
    def _erstelle_rechnungen_ui(self):
        """Erstellt die Rechnungen-UI"""
        from view.rechnungen_view import RechnungenView
        self.rechnungen_view = RechnungenView(self.rechnungen_frame, self.manager)
    
    def _oeffne_kunden(self):
        """Öffnet den Kunden-Tab"""
        self.notebook.select(1)
    
    def _oeffne_auftraege(self):
        """Öffnet den Aufträge-Tab"""
        self.notebook.select(2)
    
    def _oeffne_rechnungen(self):
        """Öffnet den Rechnungen-Tab"""
        self.notebook.select(3)
    
    def _oeffne_einstellungen(self):
        """Öffnet den Einstellungsdialog"""
        from view.einstellungen_dialog import EinstellungenDialog
        dialog = EinstellungenDialog(self.root, self.manager)
        if dialog.result:
            self.aktualisiere_uebersicht()
    
    def aktualisiere_uebersicht(self):
        """Aktualisiert die Übersicht"""
        self.notebook.forget(0)
        self.uebersicht_frame = ttk.Frame(self.notebook)
        self.notebook.insert(0, self.uebersicht_frame, text="Übersicht")
        self._erstelle_uebersicht()

