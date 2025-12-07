"""
Dialog für Positionen
"""
import tkinter as tk
from tkinter import ttk, messagebox
from model.auftrag import Position


class PositionDialog:
    """Dialog zum Erstellen/Bearbeiten von Positionen"""
    
    def __init__(self, parent: tk.Widget, position: Position = None):
        self.position = position
        self._old_position = None
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Position bearbeiten" if position else "Neue Position")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._erstelle_ui()
        
        if position:
            self._lade_position()
        
        self.dialog.wait_window()
    
    def _erstelle_ui(self):
        """Erstellt die Benutzeroberfläche"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Bezeichnung
        ttk.Label(main_frame, text="Bezeichnung *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.bezeichnung_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.bezeichnung_var, width=30).grid(row=0, column=1, pady=5, sticky=tk.EW)
        
        # Menge
        ttk.Label(main_frame, text="Menge:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.menge_var = tk.StringVar(value="1.0")
        ttk.Entry(main_frame, textvariable=self.menge_var, width=30).grid(row=1, column=1, pady=5, sticky=tk.EW)
        
        # Einheit
        ttk.Label(main_frame, text="Einheit:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.einheit_var = tk.StringVar(value="Stk")
        einheit_combo = ttk.Combobox(main_frame, textvariable=self.einheit_var, 
                                    values=["Stk", "Std", "Tag", "m", "m²", "m³", "kg", "t"], 
                                    width=27, state="readonly")
        einheit_combo.grid(row=2, column=1, pady=5, sticky=tk.EW)
        
        # Einzelpreis
        ttk.Label(main_frame, text="Einzelpreis (€):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.einzelpreis_var = tk.StringVar(value="0.00")
        ttk.Entry(main_frame, textvariable=self.einzelpreis_var, width=30).grid(row=3, column=1, pady=5, sticky=tk.EW)
        
        # Gesamtpreis (berechnet)
        ttk.Label(main_frame, text="Gesamtpreis:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.gesamtpreis_label = ttk.Label(main_frame, text="0,00 €", font=("Arial", 10))
        self.gesamtpreis_label.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Berechnung bei Änderung
        self.menge_var.trace("w", lambda *args: self._berechnen())
        self.einzelpreis_var.trace("w", lambda *args: self._berechnen())
        
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Abbrechen", command=self._abbrechen).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Speichern", command=self._speichern).pack(side=tk.RIGHT, padx=5)
    
    def _lade_position(self):
        """Lädt Positionsdaten in die Felder"""
        if not self.position:
            return
        
        # Alte Position speichern für ID-Übernahme
        self._old_position = self.position
        
        self.bezeichnung_var.set(self.position.bezeichnung)
        self.menge_var.set(str(self.position.menge))
        self.einheit_var.set(self.position.einheit)
        self.einzelpreis_var.set(str(self.position.einzelpreis))
        self._berechnen()
    
    def _berechnen(self):
        """Berechnet den Gesamtpreis"""
        try:
            menge = float(self.menge_var.get() or 0)
            einzelpreis = float(self.einzelpreis_var.get() or 0)
            gesamt = menge * einzelpreis
            self.gesamtpreis_label.config(text=f"{gesamt:.2f} €")
        except ValueError:
            self.gesamtpreis_label.config(text="0,00 €")
    
    def _speichern(self):
        """Speichert die Position"""
        if not self.bezeichnung_var.get().strip():
            messagebox.showerror("Fehler", "Bezeichnung ist erforderlich.")
            return
        
        try:
            menge = float(self.menge_var.get() or 1.0)
            einzelpreis = float(self.einzelpreis_var.get() or 0.0)
        except ValueError:
            messagebox.showerror("Fehler", "Menge und Einzelpreis müssen Zahlen sein.")
            return
        
        self.position = Position(
            bezeichnung=self.bezeichnung_var.get().strip(),
            menge=menge,
            einheit=self.einheit_var.get(),
            einzelpreis=einzelpreis
        )
        
        # ID von alter Position übernehmen, falls vorhanden
        if self.position and hasattr(self, '_old_position') and self._old_position:
            self.position.id = self._old_position.id
        
        self.result = True
        self.dialog.destroy()
    
    def _abbrechen(self):
        """Bricht den Dialog ab"""
        self.dialog.destroy()

