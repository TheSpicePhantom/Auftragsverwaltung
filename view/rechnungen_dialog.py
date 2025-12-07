"""
Dialog für Rechnungsbearbeitung
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from adapter.manager import DatenManager
from model.rechnung import Rechnung


class RechnungenDialog:
    """Dialog zum Bearbeiten von Rechnungen"""
    
    def __init__(self, parent: tk.Widget, manager: DatenManager, rechnung: Rechnung):
        self.manager = manager
        self.rechnung = rechnung
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Rechnung bearbeiten")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._erstelle_ui()
        self._lade_rechnung()
        
        self.dialog.wait_window()
    
    def _erstelle_ui(self):
        """Erstellt die Benutzeroberfläche"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Rechnungsnummer
        ttk.Label(main_frame, text="Rechnungsnummer:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.rechnungsnummer_label = ttk.Label(main_frame, text="", font=("Arial", 10, "bold"))
        self.rechnungsnummer_label.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Kunde
        kunde = self.manager.get_kunde(self.rechnung.kunde_id)
        kunde_name = kunde.get_vollstaendiger_name() if kunde else "Unbekannt"
        ttk.Label(main_frame, text="Kunde:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text=kunde_name).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Rechnungsdatum
        ttk.Label(main_frame, text="Rechnungsdatum:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.rechnungsdatum_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.rechnungsdatum_var, width=30).grid(row=2, column=1, pady=5, sticky=tk.EW)
        
        # Fälligkeitsdatum
        ttk.Label(main_frame, text="Fälligkeitsdatum:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.faelligkeitsdatum_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.faelligkeitsdatum_var, width=30).grid(row=3, column=1, pady=5, sticky=tk.EW)
        
        # Status
        ttk.Label(main_frame, text="Status:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(main_frame, textvariable=self.status_var, 
                                    values=["Offen", "Bezahlt", "Überfällig", "Storniert"], 
                                    state="readonly", width=27)
        status_combo.grid(row=4, column=1, pady=5, sticky=tk.EW)
        
        # Zahlungsart
        ttk.Label(main_frame, text="Zahlungsart:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.zahlungsart_var = tk.StringVar()
        config = self.manager.adapter.get_config()
        zahlungsarten = config.get("rechnung", {}).get("zahlungsarten", ["Überweisung", "Bar", "Scheck"])
        zahlungsart_combo = ttk.Combobox(main_frame, textvariable=self.zahlungsart_var, 
                                        values=zahlungsarten, state="readonly", width=27)
        zahlungsart_combo.grid(row=5, column=1, pady=5, sticky=tk.EW)
        
        # Positionen (nur Anzeige)
        ttk.Label(main_frame, text="Positionen:").grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        pos_frame = ttk.Frame(main_frame)
        pos_frame.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        vsb = ttk.Scrollbar(pos_frame, orient=tk.VERTICAL)
        self.pos_tree = ttk.Treeview(pos_frame, columns=("Menge", "Einheit", "Einzelpreis", "Gesamtpreis"), 
                                     show="tree headings", yscrollcommand=vsb.set, height=6)
        vsb.config(command=self.pos_tree.yview)
        
        self.pos_tree.heading("#0", text="Bezeichnung")
        self.pos_tree.heading("Menge", text="Menge")
        self.pos_tree.heading("Einheit", text="Einheit")
        self.pos_tree.heading("Einzelpreis", text="Einzelpreis")
        self.pos_tree.heading("Gesamtpreis", text="Gesamtpreis")
        
        self.pos_tree.column("#0", width=200)
        self.pos_tree.column("Menge", width=60)
        self.pos_tree.column("Einheit", width=60)
        self.pos_tree.column("Einzelpreis", width=100)
        self.pos_tree.column("Gesamtpreis", width=100)
        
        self.pos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Beträge
        betraege_frame = ttk.Frame(main_frame)
        betraege_frame.grid(row=8, column=0, columnspan=2, sticky=tk.E, pady=5)
        
        self.betraege_label = ttk.Label(betraege_frame, text="", font=("Arial", 10))
        self.betraege_label.pack(side=tk.RIGHT)
        
        # Notizen
        ttk.Label(main_frame, text="Notizen:").grid(row=9, column=0, sticky=tk.NW, pady=5)
        self.notizen_text = tk.Text(main_frame, width=40, height=3)
        self.notizen_text.grid(row=9, column=1, pady=5, sticky=tk.EW)
        
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Abbrechen", command=self._abbrechen).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Speichern", command=self._speichern).pack(side=tk.RIGHT, padx=5)
    
    def _lade_rechnung(self):
        """Lädt Rechnungsdaten in die Felder"""
        self.rechnungsnummer_label.config(text=self.rechnung.rechnungsnummer)
        self.rechnungsdatum_var.set(self.rechnung.rechnungsdatum.strftime("%d.%m.%Y"))
        self.faelligkeitsdatum_var.set(self.rechnung.faelligkeitsdatum.strftime("%d.%m.%Y"))
        self.status_var.set(self.rechnung.status)
        self.zahlungsart_var.set(self.rechnung.zahlungsart)
        self.notizen_text.delete("1.0", tk.END)
        self.notizen_text.insert("1.0", self.rechnung.notizen)
        
        # Positionen laden
        for pos in self.rechnung.positionen:
            self.pos_tree.insert("", tk.END, text=pos.bezeichnung,
                               values=(pos.menge, pos.einheit, f"{pos.einzelpreis:.2f} €", f"{pos.gesamtpreis:.2f} €"))
        
        # Beträge anzeigen
        self.rechnung._berechnen()
        text = f"Netto: {self.rechnung.nettobetrag:.2f} € | MwSt: {self.rechnung.mwst_betrag:.2f} € | Brutto: {self.rechnung.bruttobetrag:.2f} €"
        self.betraege_label.config(text=text)
    
    def _speichern(self):
        """Speichert die Rechnung"""
        try:
            # Datum parsen
            rechnungsdatum = datetime.strptime(self.rechnungsdatum_var.get(), "%d.%m.%Y")
            faelligkeitsdatum = datetime.strptime(self.faelligkeitsdatum_var.get(), "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie gültige Datumsformate ein (TT.MM.JJJJ).")
            return
        
        self.rechnung.rechnungsdatum = rechnungsdatum
        self.rechnung.faelligkeitsdatum = faelligkeitsdatum
        self.rechnung.status = self.status_var.get()
        self.rechnung.zahlungsart = self.zahlungsart_var.get()
        self.rechnung.notizen = self.notizen_text.get("1.0", tk.END).strip()
        
        self.manager.update_rechnung(self.rechnung)
        self.result = True
        self.dialog.destroy()
    
    def _abbrechen(self):
        """Bricht den Dialog ab"""
        self.dialog.destroy()


