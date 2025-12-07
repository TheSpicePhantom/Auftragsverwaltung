"""
Dialog für Stücklisten-Bearbeitung
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional
from adapter.manager import DatenManager
from model.stueckliste import Stueckliste, StuecklistenEintrag
from model.auftrag import Auftrag
from model.kunde import Kunde


class StuecklisteDialog:
    """Dialog zum Erstellen/Bearbeiten von Stücklisten"""
    
    def __init__(self, parent: tk.Widget, manager: DatenManager, auftrag: Auftrag, position_id: str):
        self.manager = manager
        self.auftrag = auftrag
        self.position_id = position_id
        self.result = False
        
        # Finde Position
        self.position = next((p for p in auftrag.positionen if p.id == position_id), None)
        if not self.position:
            messagebox.showerror("Fehler", "Position nicht gefunden.")
            return
        
        # Lade oder erstelle Stückliste
        self.stueckliste = manager.get_stueckliste_fuer_position(auftrag.id, position_id)
        if not self.stueckliste:
            # Neue Stückliste erstellen
            kunde = manager.get_kunde(auftrag.kunde_id)
            self.stueckliste = Stueckliste(
                auftrag_id=auftrag.id,
                position_id=position_id,
                projekt=self.position.bezeichnung,
                kunde_id=auftrag.kunde_id,
                auftragsnummer=auftrag.auftragsnummer
            )
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Stückliste - {self.position.bezeichnung}")
        self.dialog.geometry("1000x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._erstelle_ui()
        self._lade_stueckliste()
        
        self.dialog.wait_window()
    
    def _erstelle_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Kopfzeile
        header_frame = ttk.LabelFrame(main_frame, text="Kopfzeile", padding=10)
        header_frame.pack(fill=tk.X, pady=5)
        
        # Projekt und Auftragsnummer
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(fill=tk.X)
        
        ttk.Label(info_frame, text="Projekt:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.projekt_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.projekt_var, width=40).grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)
        
        ttk.Label(info_frame, text="Auftragsnummer:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.auftragsnummer_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.auftragsnummer_var, width=30, state="readonly").grid(row=0, column=3, padx=5, pady=2, sticky=tk.EW)
        
        ttk.Label(info_frame, text="Kunde:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.kunde_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.kunde_var, width=40, state="readonly").grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)
        
        ttk.Label(info_frame, text="Stücklistennummer:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.stuecklisten_nummer_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.stuecklisten_nummer_var, width=30, state="readonly").grid(row=1, column=3, padx=5, pady=2, sticky=tk.EW)
        
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid_columnconfigure(3, weight=1)
        
        # Einträge-Tabelle
        eintraege_frame = ttk.LabelFrame(main_frame, text="Materialeinträge", padding=10)
        eintraege_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview für Einträge
        tree_frame = ttk.Frame(eintraege_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.eintraege_tree = ttk.Treeview(
            tree_frame,
            columns=("Material", "Menge", "Einheit", "Einzelpreis", "Gesamtpreis", "Beschreibung"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=10
        )
        
        vsb.config(command=self.eintraege_tree.yview)
        hsb.config(command=self.eintraege_tree.xview)
        
        # Spalten definieren
        self.eintraege_tree.heading("Material", text="Material")
        self.eintraege_tree.heading("Menge", text="Menge")
        self.eintraege_tree.heading("Einheit", text="Einheit")
        self.eintraege_tree.heading("Einzelpreis", text="Einzelpreis (€)")
        self.eintraege_tree.heading("Gesamtpreis", text="Gesamtpreis (€)")
        self.eintraege_tree.heading("Beschreibung", text="Beschreibung")
        
        self.eintraege_tree.column("Material", width=200)
        self.eintraege_tree.column("Menge", width=80)
        self.eintraege_tree.column("Einheit", width=80)
        self.eintraege_tree.column("Einzelpreis", width=120)
        self.eintraege_tree.column("Gesamtpreis", width=120)
        self.eintraege_tree.column("Beschreibung", width=300)
        
        self.eintraege_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons für Einträge
        eintraege_button_frame = ttk.Frame(eintraege_frame)
        eintraege_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(eintraege_button_frame, text="Eintrag hinzufügen", command=self._eintrag_hinzufuegen).pack(side=tk.LEFT, padx=2)
        ttk.Button(eintraege_button_frame, text="Eintrag bearbeiten", command=self._eintrag_bearbeiten).pack(side=tk.LEFT, padx=2)
        ttk.Button(eintraege_button_frame, text="Eintrag löschen", command=self._eintrag_loeschen).pack(side=tk.LEFT, padx=2)
        
        # Gesamtbetrag
        gesamt_frame = ttk.Frame(eintraege_frame)
        gesamt_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(gesamt_frame, text="Gesamtbetrag:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.gesamtbetrag_label = ttk.Label(gesamt_frame, text="0,00 €", font=("Arial", 12, "bold"))
        self.gesamtbetrag_label.pack(side=tk.LEFT, padx=5)
        
        # Notizen
        notizen_frame = ttk.LabelFrame(main_frame, text="Notizen", padding=10)
        notizen_frame.pack(fill=tk.X, pady=5)
        
        self.notizen_text = tk.Text(notizen_frame, width=80, height=3)
        self.notizen_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Drucken (PDF)", command=self._drucken).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Abbrechen", command=self._abbrechen).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Speichern", command=self._speichern).pack(side=tk.RIGHT, padx=5)
    
    def _lade_stueckliste(self):
        """Lädt Stücklistendaten in die Felder"""
        if not self.stueckliste:
            return
        
        self.projekt_var.set(self.stueckliste.projekt)
        self.auftragsnummer_var.set(self.stueckliste.auftragsnummer)
        self.stuecklisten_nummer_var.set(self.stueckliste.stuecklisten_nummer or "")
        self.notizen_text.delete("1.0", tk.END)
        self.notizen_text.insert("1.0", self.stueckliste.notizen)
        
        # Kunde laden
        kunde = self.manager.get_kunde(self.auftrag.kunde_id)
        if kunde:
            self.kunde_var.set(kunde.get_vollstaendiger_name())
        
        # Einträge laden
        self._aktualisiere_eintraege_liste()
    
    def _aktualisiere_eintraege_liste(self):
        """Aktualisiert die Einträge-Liste"""
        for item in self.eintraege_tree.get_children():
            self.eintraege_tree.delete(item)
        
        if self.stueckliste:
            for eintrag in self.stueckliste.eintraege:
                self.eintraege_tree.insert("", tk.END, iid=eintrag.id,
                                          values=(eintrag.material,
                                                 f"{eintrag.menge:.2f}",
                                                 eintrag.einheit,
                                                 f"{eintrag.einzelpreis:.2f}",
                                                 f"{eintrag.gesamtpreis:.2f}",
                                                 eintrag.beschreibung))
        
        # Gesamtbetrag aktualisieren
        gesamtbetrag = self.stueckliste.get_gesamtbetrag() if self.stueckliste else 0.0
        self.gesamtbetrag_label.config(text=f"{gesamtbetrag:.2f} €")
    
    def _eintrag_hinzufuegen(self):
        """Fügt einen neuen Eintrag hinzu"""
        dialog = StuecklistenEintragDialog(self.dialog)
        if dialog.result and dialog.eintrag:
            self.stueckliste.add_eintrag(dialog.eintrag)
            self._aktualisiere_eintraege_liste()
    
    def _eintrag_bearbeiten(self):
        """Bearbeitet einen ausgewählten Eintrag"""
        selection = self.eintraege_tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Eintrag aus.")
            return
        
        eintrag_id = selection[0]
        eintrag = next((e for e in self.stueckliste.eintraege if e.id == eintrag_id), None)
        
        if eintrag:
            dialog = StuecklistenEintragDialog(self.dialog, eintrag)
            if dialog.result and dialog.eintrag:
                # Eintrag aktualisieren
                for i, e in enumerate(self.stueckliste.eintraege):
                    if e.id == eintrag_id:
                        self.stueckliste.eintraege[i] = dialog.eintrag
                        break
                self._aktualisiere_eintraege_liste()
    
    def _eintrag_loeschen(self):
        """Löscht einen ausgewählten Eintrag"""
        selection = self.eintraege_tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Eintrag aus.")
            return
        
        eintrag_id = selection[0]
        if messagebox.askyesno("Löschen", "Möchten Sie diesen Eintrag wirklich löschen?"):
            self.stueckliste.remove_eintrag(eintrag_id)
            self._aktualisiere_eintraege_liste()
    
    def _speichern(self):
        """Speichert die Stückliste"""
        # Daten aktualisieren
        self.stueckliste.projekt = self.projekt_var.get()
        self.stueckliste.notizen = self.notizen_text.get("1.0", tk.END).strip()
        
        # Stücklistennummer generieren, falls noch nicht vorhanden
        if not self.stueckliste.stuecklisten_nummer:
            self.stueckliste.stuecklisten_nummer = self.stueckliste._generate_stuecklisten_nummer()
            self.stuecklisten_nummer_var.set(self.stueckliste.stuecklisten_nummer)
        
        # Speichern
        if self.manager.get_stueckliste(self.stueckliste.id):
            self.manager.update_stueckliste(self.stueckliste)
        else:
            self.manager.add_stueckliste(self.stueckliste)
        
        self.result = True
        messagebox.showinfo("Erfolg", "Stückliste wurde gespeichert.")
    
    def _drucken(self):
        """Erstellt PDF der Stückliste"""
        # Zuerst speichern
        self._speichern()
        
        # PDF generieren
        try:
            from adapter.pdf_generator import PDFGenerator
            generator = PDFGenerator(self.manager)
            output_path = generator.erstelle_stueckliste_pdf(self.stueckliste)
            messagebox.showinfo("Erfolg", f"PDF wurde erstellt:\n{output_path}")
        except ImportError:
            messagebox.showerror("Fehler", "PDF-Generator konnte nicht geladen werden. Bitte installieren Sie reportlab:\npip install reportlab")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des PDFs:\n{str(e)}")
    
    def _abbrechen(self):
        """Bricht den Dialog ab"""
        self.dialog.destroy()


class StuecklistenEintragDialog:
    """Dialog zum Erstellen/Bearbeiten von Stücklisten-Einträgen"""
    
    def __init__(self, parent: tk.Widget, eintrag: StuecklistenEintrag = None):
        self.eintrag = eintrag
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Eintrag bearbeiten" if eintrag else "Neuer Eintrag")
        self.dialog.geometry("500x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._erstelle_ui()
        
        if eintrag:
            self._lade_eintrag()
        
        self.dialog.wait_window()
    
    def _erstelle_ui(self):
        """Erstellt die Benutzeroberfläche"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Material
        ttk.Label(main_frame, text="Material *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.material_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.material_var, width=40).grid(row=0, column=1, pady=5, sticky=tk.EW)
        
        # Menge
        ttk.Label(main_frame, text="Menge *:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.menge_var = tk.StringVar(value="1.0")
        ttk.Entry(main_frame, textvariable=self.menge_var, width=40).grid(row=1, column=1, pady=5, sticky=tk.EW)
        
        # Einheit
        ttk.Label(main_frame, text="Einheit:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.einheit_var = tk.StringVar(value="Stk")
        ttk.Entry(main_frame, textvariable=self.einheit_var, width=40).grid(row=2, column=1, pady=5, sticky=tk.EW)
        
        # Einzelpreis
        ttk.Label(main_frame, text="Einzelpreis (€) *:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.einzelpreis_var = tk.StringVar(value="0.0")
        ttk.Entry(main_frame, textvariable=self.einzelpreis_var, width=40).grid(row=3, column=1, pady=5, sticky=tk.EW)
        
        # Beschreibung
        ttk.Label(main_frame, text="Beschreibung:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.beschreibung_text = tk.Text(main_frame, width=40, height=6)
        self.beschreibung_text.grid(row=4, column=1, pady=5, sticky=tk.EW)
        
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Abbrechen", command=self._abbrechen).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Speichern", command=self._speichern).pack(side=tk.RIGHT, padx=5)
    
    def _lade_eintrag(self):
        """Lädt Eintragsdaten in die Felder"""
        if not self.eintrag:
            return
        
        self.material_var.set(self.eintrag.material)
        self.menge_var.set(str(self.eintrag.menge))
        self.einheit_var.set(self.eintrag.einheit)
        self.einzelpreis_var.set(str(self.eintrag.einzelpreis))
        self.beschreibung_text.delete("1.0", tk.END)
        self.beschreibung_text.insert("1.0", self.eintrag.beschreibung)
    
    def _speichern(self):
        """Speichert den Eintrag"""
        # Validierung
        if not self.material_var.get().strip():
            messagebox.showerror("Fehler", "Material ist erforderlich.")
            return
        
        try:
            menge = float(self.menge_var.get() or 0.0)
            einzelpreis = float(self.einzelpreis_var.get() or 0.0)
        except ValueError:
            messagebox.showerror("Fehler", "Menge und Einzelpreis müssen Zahlen sein.")
            return
        
        # Eintrag erstellen oder aktualisieren
        if self.eintrag:
            self.eintrag.material = self.material_var.get().strip()
            self.eintrag.menge = menge
            self.eintrag.einheit = self.einheit_var.get().strip() or "Stk"
            self.eintrag.einzelpreis = einzelpreis
            self.eintrag.beschreibung = self.beschreibung_text.get("1.0", tk.END).strip()
            self.eintrag.berechne_gesamtpreis()
        else:
            self.eintrag = StuecklistenEintrag(
                material=self.material_var.get().strip(),
                menge=menge,
                einheit=self.einheit_var.get().strip() or "Stk",
                einzelpreis=einzelpreis,
                beschreibung=self.beschreibung_text.get("1.0", tk.END).strip()
            )
        
        self.result = True
        self.dialog.destroy()
    
    def _abbrechen(self):
        """Bricht den Dialog ab"""
        self.dialog.destroy()

