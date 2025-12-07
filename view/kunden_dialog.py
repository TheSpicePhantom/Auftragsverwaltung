"""
Dialog für Kundenbearbeitung
"""
import tkinter as tk
from tkinter import ttk, messagebox
from adapter.manager import DatenManager
from model.kunde import Kunde


class KundenDialog:
    """Dialog zum Erstellen/Bearbeiten von Kunden"""
    
    def __init__(self, parent: tk.Widget, manager: DatenManager, kunde: Kunde = None):
        self.manager = manager
        self.kunde = kunde
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Kunde bearbeiten" if kunde else "Neuer Kunde")
        self.dialog.geometry("500x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._erstelle_ui()
        
        if kunde:
            self._lade_kunde()
        
        self.dialog.wait_window()
    
    def _erstelle_ui(self):
        """Erstellt die Benutzeroberfläche"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(main_frame, text="Name *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=5, sticky=tk.EW)
        
        # Vorname
        ttk.Label(main_frame, text="Vorname:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.vorname_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.vorname_var, width=40).grid(row=1, column=1, pady=5, sticky=tk.EW)
        
        # Firma
        ttk.Label(main_frame, text="Firma:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.firma_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.firma_var, width=40).grid(row=2, column=1, pady=5, sticky=tk.EW)
        
        # Adresse
        ttk.Label(main_frame, text="Straße:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.strasse_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.strasse_var, width=40).grid(row=3, column=1, pady=5, sticky=tk.EW)
        
        ttk.Label(main_frame, text="PLZ:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.plz_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.plz_var, width=40).grid(row=4, column=1, pady=5, sticky=tk.EW)
        
        ttk.Label(main_frame, text="Ort:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.ort_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.ort_var, width=40).grid(row=5, column=1, pady=5, sticky=tk.EW)
        
        # Kontakt
        ttk.Label(main_frame, text="Telefon:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.telefon_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.telefon_var, width=40).grid(row=6, column=1, pady=5, sticky=tk.EW)
        
        ttk.Label(main_frame, text="E-Mail:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.email_var, width=40).grid(row=7, column=1, pady=5, sticky=tk.EW)
        
        # USt-ID
        ttk.Label(main_frame, text="USt-ID:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.ust_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.ust_id_var, width=40).grid(row=8, column=1, pady=5, sticky=tk.EW)
        
        # Konditionen
        konditionen_frame = ttk.LabelFrame(main_frame, text="Konditionen (in %)", padding=5)
        konditionen_frame.grid(row=9, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        ttk.Label(konditionen_frame, text="Skonto:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.skonto_var = tk.StringVar(value="0.0")
        ttk.Entry(konditionen_frame, textvariable=self.skonto_var, width=15).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(konditionen_frame, text="%").grid(row=0, column=2, sticky=tk.W, padx=2)
        
        ttk.Label(konditionen_frame, text="Abschlag:").grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        self.abschlag_var = tk.StringVar(value="0.0")
        ttk.Entry(konditionen_frame, textvariable=self.abschlag_var, width=15).grid(row=0, column=4, padx=5, pady=2, sticky=tk.W)
        ttk.Label(konditionen_frame, text="%").grid(row=0, column=5, sticky=tk.W, padx=2)
        
        ttk.Label(konditionen_frame, text="Rabatt:").grid(row=0, column=6, sticky=tk.W, padx=5, pady=2)
        self.rabatt_var = tk.StringVar(value="0.0")
        ttk.Entry(konditionen_frame, textvariable=self.rabatt_var, width=15).grid(row=0, column=7, padx=5, pady=2, sticky=tk.W)
        ttk.Label(konditionen_frame, text="%").grid(row=0, column=8, sticky=tk.W, padx=2)
        
        # Notizen
        ttk.Label(main_frame, text="Notizen:").grid(row=10, column=0, sticky=tk.NW, pady=5)
        self.notizen_text = tk.Text(main_frame, width=40, height=5)
        self.notizen_text.grid(row=10, column=1, pady=5, sticky=tk.EW)
        
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Abbrechen", command=self._abbrechen).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Speichern", command=self._speichern).pack(side=tk.RIGHT, padx=5)
    
    def _lade_kunde(self):
        """Lädt Kundendaten in die Felder"""
        if not self.kunde:
            return
        
        self.name_var.set(self.kunde.name)
        self.vorname_var.set(self.kunde.vorname)
        self.firma_var.set(self.kunde.firma)
        self.strasse_var.set(self.kunde.strasse)
        self.plz_var.set(self.kunde.plz)
        self.ort_var.set(self.kunde.ort)
        self.telefon_var.set(self.kunde.telefon)
        self.email_var.set(self.kunde.email)
        self.ust_id_var.set(self.kunde.ust_id)
        self.skonto_var.set(str(self.kunde.skonto))
        self.abschlag_var.set(str(self.kunde.abschlag))
        self.rabatt_var.set(str(self.kunde.rabatt))
        self.notizen_text.delete("1.0", tk.END)
        self.notizen_text.insert("1.0", self.kunde.notizen)
    
    def _speichern(self):
        """Speichert den Kunden"""
        if not self.name_var.get().strip():
            messagebox.showerror("Fehler", "Name ist erforderlich.")
            return
        
        # Konditionen validieren
        try:
            skonto = float(self.skonto_var.get() or 0.0)
            abschlag = float(self.abschlag_var.get() or 0.0)
            rabatt = float(self.rabatt_var.get() or 0.0)
        except ValueError:
            messagebox.showerror("Fehler", "Konditionen müssen Zahlen sein.")
            return
        
        kunde = Kunde(
            name=self.name_var.get().strip(),
            vorname=self.vorname_var.get().strip(),
            firma=self.firma_var.get().strip(),
            strasse=self.strasse_var.get().strip(),
            plz=self.plz_var.get().strip(),
            ort=self.ort_var.get().strip(),
            telefon=self.telefon_var.get().strip(),
            email=self.email_var.get().strip(),
            ust_id=self.ust_id_var.get().strip(),
            notizen=self.notizen_text.get("1.0", tk.END).strip(),
            skonto=skonto,
            abschlag=abschlag,
            rabatt=rabatt
        )
        
        if self.kunde:
            kunde.id = self.kunde.id
            kunde.erstellt_am = self.kunde.erstellt_am
            self.manager.update_kunde(kunde)
        else:
            self.manager.add_kunde(kunde)
        
        self.result = True
        self.dialog.destroy()
    
    def _abbrechen(self):
        """Bricht den Dialog ab"""
        self.dialog.destroy()


