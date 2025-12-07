"""
Dialog für Auftragsbearbeitung
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from adapter.manager import DatenManager
from model.auftrag import Auftrag, Position
from view.position_dialog import PositionDialog


class AuftraegeDialog:
    """Dialog zum Erstellen/Bearbeiten von Aufträgen"""
    
    def __init__(self, parent: tk.Widget, manager: DatenManager, auftrag: Auftrag = None):
        self.manager = manager
        self.auftrag = auftrag
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Auftrag bearbeiten" if auftrag else "Neuer Auftrag")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._erstelle_ui()
        
        if auftrag:
            self._lade_auftrag()
        else:
            # Vorschau der nächsten Auftragsnummer
            naechste_nummer = self.manager.generiere_naechste_auftragsnummer()
            self.auftragsnummer_var.set(naechste_nummer)
        
        self.dialog.wait_window()
    
    def _erstelle_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Hauptframe mit Scrollbar
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(scrollable_frame, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Auftragsnummer
        ttk.Label(main_frame, text="Auftragsnummer:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.auftragsnummer_var = tk.StringVar()
        auftragsnummer_entry = ttk.Entry(main_frame, textvariable=self.auftragsnummer_var, width=30, state="readonly")
        auftragsnummer_entry.grid(row=0, column=1, pady=5, sticky=tk.EW)
        
        # Kunde
        ttk.Label(main_frame, text="Kunde *:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.kunde_var = tk.StringVar()
        kunden = self.manager.get_kunden()
        kunden_namen = [k.get_vollstaendiger_name() for k in kunden]
        kunde_combo = ttk.Combobox(main_frame, textvariable=self.kunde_var, values=kunden_namen, width=27)
        kunde_combo.grid(row=1, column=1, pady=5, sticky=tk.EW)
        self.kunde_combo = kunde_combo
        
        # Bezeichnung
        ttk.Label(main_frame, text="Bezeichnung *:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.bezeichnung_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.bezeichnung_var, width=30).grid(row=2, column=1, pady=5, sticky=tk.EW)
        
        # Beschreibung
        ttk.Label(main_frame, text="Beschreibung:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.beschreibung_text = tk.Text(main_frame, width=30, height=4)
        self.beschreibung_text.grid(row=3, column=1, pady=5, sticky=tk.EW)
        
        # Status
        ttk.Label(main_frame, text="Status:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar()
        config = self.manager.adapter.get_config()
        status_optionen = config.get("auftrag", {}).get("status_optionen", ["Angebot", "Bestätigt", "In Bearbeitung", "Abgeschlossen", "Storniert"])
        status_combo = ttk.Combobox(main_frame, textvariable=self.status_var, values=status_optionen, state="readonly", width=27)
        status_combo.grid(row=4, column=1, pady=5, sticky=tk.EW)
        status_combo.set(status_optionen[0] if status_optionen else "Angebot")
        
        # Fälligkeitsdatum
        ttk.Label(main_frame, text="Fälligkeitsdatum:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.faellig_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.faellig_var, width=30).grid(row=5, column=1, pady=5, sticky=tk.EW)
        ttk.Label(main_frame, text="(Format: TT.MM.JJJJ)", font=("Arial", 8)).grid(row=6, column=1, sticky=tk.W)
        
        # MwSt-Satz
        ttk.Label(main_frame, text="MwSt-Satz (%):").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.mwst_var = tk.StringVar(value="19.0")
        ttk.Entry(main_frame, textvariable=self.mwst_var, width=30).grid(row=7, column=1, pady=5, sticky=tk.EW)
        
        # Positionen
        ttk.Label(main_frame, text="Positionen:").grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Positionen-Liste
        pos_frame = ttk.Frame(main_frame)
        pos_frame.grid(row=9, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        pos_list_frame = ttk.Frame(pos_frame)
        pos_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview für Positionen
        pos_tree_scroll = ttk.Scrollbar(pos_list_frame, orient=tk.VERTICAL)
        self.pos_tree = ttk.Treeview(pos_list_frame, columns=("Menge", "Einheit", "Einzelpreis", "Gesamtpreis"), 
                                     show="tree headings", height=5, yscrollcommand=pos_tree_scroll.set)
        pos_tree_scroll.config(command=self.pos_tree.yview)
        
        self.pos_tree.heading("#0", text="Bezeichnung")
        self.pos_tree.heading("Menge", text="Menge")
        self.pos_tree.heading("Einheit", text="Einheit")
        self.pos_tree.heading("Einzelpreis", text="Einzelpreis")
        self.pos_tree.heading("Gesamtpreis", text="Gesamtpreis")
        
        self.pos_tree.column("#0", width=200)
        self.pos_tree.column("Menge", width=80)
        self.pos_tree.column("Einheit", width=80)
        self.pos_tree.column("Einzelpreis", width=100)
        self.pos_tree.column("Gesamtpreis", width=100)
        
        self.pos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pos_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons für Positionen
        pos_button_frame = ttk.Frame(pos_frame)
        pos_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(pos_button_frame, text="Position hinzufügen", command=self._position_hinzufuegen).pack(side=tk.LEFT, padx=2)
        ttk.Button(pos_button_frame, text="Position bearbeiten", command=self._position_bearbeiten).pack(side=tk.LEFT, padx=2)
        ttk.Button(pos_button_frame, text="Position löschen", command=self._position_loeschen).pack(side=tk.LEFT, padx=2)
        
        # Gesamtpreise
        ttk.Label(main_frame, text="Gesamtpreis (netto):").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.gesamtpreis_label = ttk.Label(main_frame, text="0,00 €", font=("Arial", 10))
        self.gesamtpreis_label.grid(row=10, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="MwSt:").grid(row=11, column=0, sticky=tk.W, pady=5)
        self.mwst_label = ttk.Label(main_frame, text="0,00 €", font=("Arial", 10))
        self.mwst_label.grid(row=11, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Endpreis (brutto):").grid(row=12, column=0, sticky=tk.W, pady=5)
        self.endpreis_label = ttk.Label(main_frame, text="0,00 €", font=("Arial", 10, "bold"))
        self.endpreis_label.grid(row=12, column=1, sticky=tk.W, pady=5)
        
        # Notizen
        ttk.Label(main_frame, text="Notizen:").grid(row=13, column=0, sticky=tk.NW, pady=5)
        self.notizen_text = tk.Text(main_frame, width=30, height=4)
        self.notizen_text.grid(row=13, column=1, pady=5, sticky=tk.EW)
        
        main_frame.grid_columnconfigure(1, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Abbrechen", command=self._abbrechen).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Speichern", command=self._speichern).pack(side=tk.RIGHT, padx=5)
        
        # Bindings für automatische Berechnung
        self.mwst_var.trace("w", lambda *args: self._berechnen())
        self.pos_tree.bind("<<TreeviewSelect>>", lambda e: self._berechnen())
    
    def _lade_auftrag(self):
        """Lädt Auftragsdaten in die Felder"""
        if not self.auftrag:
            return
        
        self.auftragsnummer_var.set(self.auftrag.auftragsnummer)
        
        kunde = self.manager.get_kunde(self.auftrag.kunde_id)
        if kunde:
            self.kunde_var.set(kunde.get_vollstaendiger_name())
        
        self.bezeichnung_var.set(self.auftrag.bezeichnung)
        self.beschreibung_text.delete("1.0", tk.END)
        self.beschreibung_text.insert("1.0", self.auftrag.beschreibung)
        self.status_var.set(self.auftrag.status)
        
        if self.auftrag.faellig_am:
            self.faellig_var.set(self.auftrag.faellig_am.strftime("%d.%m.%Y"))
        
        self.mwst_var.set(str(self.auftrag.mwst_satz))
        self.notizen_text.delete("1.0", tk.END)
        self.notizen_text.insert("1.0", self.auftrag.notizen)
        
        # Positionen laden
        self._aktualisiere_positionen_liste()
        self._berechnen()
    
    def _aktualisiere_positionen_liste(self):
        """Aktualisiert die Positionen-Liste"""
        for item in self.pos_tree.get_children():
            self.pos_tree.delete(item)
        
        if self.auftrag:
            for pos in self.auftrag.positionen:
                self.pos_tree.insert("", tk.END, iid=pos.id, text=pos.bezeichnung,
                                   values=(f"{pos.menge:.2f}", pos.einheit, 
                                          f"{pos.einzelpreis:.2f} €", f"{pos.gesamtpreis:.2f} €"))
    
    def _position_hinzufuegen(self):
        """Fügt eine neue Position hinzu"""
        dialog = PositionDialog(self.dialog)
        if dialog.result and dialog.position:
            if not self.auftrag:
                # Temporären Auftrag erstellen für Positionen-Verwaltung
                kunde_id = self._get_selected_kunde_id()
                if not kunde_id:
                    messagebox.showwarning("Kein Kunde", "Bitte wählen Sie zuerst einen Kunden aus.")
                    return
                self.auftrag = Auftrag(
                    kunde_id=kunde_id,
                    bezeichnung=self.bezeichnung_var.get() or "Temporär",
                    auftragsnummer=self.auftragsnummer_var.get()
                )
            
            self.auftrag.add_position(dialog.position)
            self._aktualisiere_positionen_liste()
            self._berechnen()
    
    def _position_bearbeiten(self):
        """Bearbeitet eine ausgewählte Position"""
        selection = self.pos_tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Position aus.")
            return
        
        if not self.auftrag:
            return
        
        position_id = selection[0]
        position = next((p for p in self.auftrag.positionen if p.id == position_id), None)
        
        if position:
            dialog = PositionDialog(self.dialog, position)
            if dialog.result and dialog.position:
                # Position aktualisieren
                for i, p in enumerate(self.auftrag.positionen):
                    if p.id == position_id:
                        self.auftrag.positionen[i] = dialog.position
                        break
                self.auftrag._berechnen()
                self._aktualisiere_positionen_liste()
                self._berechnen()
    
    def _position_loeschen(self):
        """Löscht eine ausgewählte Position"""
        selection = self.pos_tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Position aus.")
            return
        
        if not self.auftrag:
            return
        
        position_id = selection[0]
        if messagebox.askyesno("Löschen", "Möchten Sie diese Position wirklich löschen?"):
            self.auftrag.remove_position(position_id)
            self._aktualisiere_positionen_liste()
            self._berechnen()
    
    def _get_selected_kunde_id(self) -> str:
        """Gibt die ID des ausgewählten Kunden zurück"""
        kunde_name = self.kunde_var.get()
        if not kunde_name:
            return None
        
        kunden = self.manager.get_kunden()
        for kunde in kunden:
            if kunde.get_vollstaendiger_name() == kunde_name:
                return kunde.id
        return None
    
    def _berechnen(self):
        """Berechnet die Gesamtpreise"""
        if not self.auftrag or not self.auftrag.positionen:
            self.gesamtpreis_label.config(text="0,00 €")
            self.mwst_label.config(text="0,00 €")
            self.endpreis_label.config(text="0,00 €")
            return
        
        self.auftrag._berechnen()
        
        try:
            mwst_satz = float(self.mwst_var.get() or 19.0)
            self.auftrag.mwst_satz = mwst_satz
            self.auftrag._berechnen()
        except ValueError:
            pass
        
        self.gesamtpreis_label.config(text=f"{self.auftrag.gesamtpreis:.2f} €")
        self.mwst_label.config(text=f"{self.auftrag.mwst_betrag:.2f} €")
        self.endpreis_label.config(text=f"{self.auftrag.endpreis:.2f} €")
    
    def _speichern(self):
        """Speichert den Auftrag"""
        # Validierung
        if not self.bezeichnung_var.get().strip():
            messagebox.showerror("Fehler", "Bezeichnung ist erforderlich.")
            return
        
        kunde_id = self._get_selected_kunde_id()
        if not kunde_id:
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Kunden aus.")
            return
        
        # Fälligkeitsdatum parsen
        faellig_am = None
        faellig_str = self.faellig_var.get().strip()
        if faellig_str:
            try:
                faellig_am = datetime.strptime(faellig_str, "%d.%m.%Y")
            except ValueError:
                messagebox.showerror("Fehler", "Ungültiges Datumsformat. Verwenden Sie TT.MM.JJJJ")
                return
        
        # MwSt-Satz parsen
        try:
            mwst_satz = float(self.mwst_var.get() or 19.0)
        except ValueError:
            messagebox.showerror("Fehler", "MwSt-Satz muss eine Zahl sein.")
            return
        
        # Auftrag erstellen oder aktualisieren
        if self.auftrag:
            # Aktualisieren
            self.auftrag.kunde_id = kunde_id
            self.auftrag.bezeichnung = self.bezeichnung_var.get().strip()
            self.auftrag.beschreibung = self.beschreibung_text.get("1.0", tk.END).strip()
            self.auftrag.status = self.status_var.get()
            self.auftrag.faellig_am = faellig_am
            self.auftrag.mwst_satz = mwst_satz
            self.auftrag.notizen = self.notizen_text.get("1.0", tk.END).strip()
            self.auftrag._berechnen()
            self.manager.update_auftrag(self.auftrag)
        else:
            # Neu erstellen
            auftragsnummer = self.auftragsnummer_var.get()
            if not auftragsnummer:
                auftragsnummer = self.manager.generiere_naechste_auftragsnummer()
            
            self.auftrag = Auftrag(
                kunde_id=kunde_id,
                bezeichnung=self.bezeichnung_var.get().strip(),
                beschreibung=self.beschreibung_text.get("1.0", tk.END).strip(),
                auftragsnummer=auftragsnummer,
                faellig_am=faellig_am,
                status=self.status_var.get(),
                mwst_satz=mwst_satz,
                notizen=self.notizen_text.get("1.0", tk.END).strip()
            )
            
            # Positionen wurden bereits in _position_hinzufuegen zum temporären Auftrag hinzugefügt
            # Der Auftrag hat bereits alle Positionen
            self.manager.add_auftrag(self.auftrag)
        
        self.result = True
        self.dialog.destroy()
    
    def _abbrechen(self):
        """Bricht den Dialog ab"""
        self.dialog.destroy()

