"""
Dialog für Stundennachweis-Bearbeitung
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, time
from typing import Optional
from adapter.manager import DatenManager
from model.stundennachweis import Stundennachweis, Zeiteintrag
from model.auftrag import Auftrag
from model.kunde import Kunde


class StundennachweisDialog:
    """Dialog zum Erstellen/Bearbeiten von Stundennachweisen"""
    
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
        
        # Lade oder erstelle Stundennachweis
        self.nachweis = manager.get_stundennachweis_fuer_position(auftrag.id, position_id)
        if not self.nachweis:
            # Neuen Nachweis erstellen
            kunde = manager.get_kunde(auftrag.kunde_id)
            self.nachweis = Stundennachweis(
                auftrag_id=auftrag.id,
                position_id=position_id,
                projekt=self.position.bezeichnung,
                kunde_id=auftrag.kunde_id,
                auftragsnummer=auftrag.auftragsnummer,
                bearbeiter=""
            )
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Stundennachweis - {self.position.bezeichnung}")
        self.dialog.geometry("1200x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._erstelle_ui()
        self._lade_nachweis()
        
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
        
        # Kopfzeile
        header_frame = ttk.LabelFrame(main_frame, text="Kopfzeile", padding=10)
        header_frame.pack(fill=tk.X, pady=5)
        
        # Links: Projekt und Kunde
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(left_frame, text="Projekt:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.projekt_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.projekt_var, width=40).grid(row=0, column=1, pady=2, sticky=tk.EW)
        
        ttk.Label(left_frame, text="Kunde:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.kunde_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.kunde_var, width=40, state="readonly").grid(row=1, column=1, pady=2, sticky=tk.EW)
        
        left_frame.grid_columnconfigure(1, weight=1)
        
        # Rechts: Auftragsnummer und Bearbeiter
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="Auftragsnummer:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.auftragsnummer_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.auftragsnummer_var, width=30, state="readonly").grid(row=0, column=1, pady=2, sticky=tk.EW)
        
        ttk.Label(right_frame, text="Bearbeiter:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.bearbeiter_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.bearbeiter_var, width=30).grid(row=1, column=1, pady=2, sticky=tk.EW)
        
        right_frame.grid_columnconfigure(1, weight=1)
        
        # Mitte: Kundenadresse
        center_frame = ttk.Frame(header_frame)
        center_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        ttk.Label(center_frame, text="Kundenadresse:").pack(anchor=tk.W)
        self.kundenadresse_label = ttk.Label(center_frame, text="", font=("Arial", 10))
        self.kundenadresse_label.pack(anchor=tk.W)
        
        # Zeiteinträge-Tabelle
        zeiten_frame = ttk.LabelFrame(main_frame, text="Zeiteinträge", padding=10)
        zeiten_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview für Zeiteinträge
        tree_frame = ttk.Frame(zeiten_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.zeiten_tree = ttk.Treeview(
            tree_frame,
            columns=("Tag", "Bearbeiter", "Start1", "End1", "Start2", "End2", "Gesamt", "Tätigkeit"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=10
        )
        
        vsb.config(command=self.zeiten_tree.yview)
        hsb.config(command=self.zeiten_tree.xview)
        
        # Spalten definieren
        self.zeiten_tree.heading("Tag", text="Datum / Tag")
        self.zeiten_tree.heading("Bearbeiter", text="Bearbeiter")
        self.zeiten_tree.heading("Start1", text="Startzeit 1")
        self.zeiten_tree.heading("End1", text="Endzeit 1")
        self.zeiten_tree.heading("Start2", text="Startzeit 2")
        self.zeiten_tree.heading("End2", text="Endzeit 2")
        self.zeiten_tree.heading("Gesamt", text="Gesamt (h)")
        self.zeiten_tree.heading("Tätigkeit", text="Tätigkeitsbeschreibung")
        
        self.zeiten_tree.column("Tag", width=120)
        self.zeiten_tree.column("Bearbeiter", width=100)
        self.zeiten_tree.column("Start1", width=80)
        self.zeiten_tree.column("End1", width=80)
        self.zeiten_tree.column("Start2", width=80)
        self.zeiten_tree.column("End2", width=80)
        self.zeiten_tree.column("Gesamt", width=80)
        self.zeiten_tree.column("Tätigkeit", width=400)
        
        self.zeiten_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons für Zeiteinträge
        zeiten_button_frame = ttk.Frame(zeiten_frame)
        zeiten_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(zeiten_button_frame, text="Zeiteintrag hinzufügen", command=self._zeiteintrag_hinzufuegen).pack(side=tk.LEFT, padx=2)
        ttk.Button(zeiten_button_frame, text="Zeiteintrag bearbeiten", command=self._zeiteintrag_bearbeiten).pack(side=tk.LEFT, padx=2)
        ttk.Button(zeiten_button_frame, text="Zeiteintrag löschen", command=self._zeiteintrag_loeschen).pack(side=tk.LEFT, padx=2)
        
        # Fußzeile
        footer_frame = ttk.LabelFrame(main_frame, text="Fußzeile", padding=10)
        footer_frame.pack(fill=tk.X, pady=5)
        
        # Reisestrecke
        reise_frame = ttk.Frame(footer_frame)
        reise_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(reise_frame, text="Reisestrecke (km):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.reisestrecke_var = tk.StringVar(value="0.0")
        ttk.Entry(reise_frame, textvariable=self.reisestrecke_var, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(reise_frame, text="Anzahl Fahrten:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.anzahl_fahrten_var = tk.StringVar(value="0")
        ttk.Entry(reise_frame, textvariable=self.anzahl_fahrten_var, width=15).grid(row=0, column=3, padx=5)
        
        ttk.Label(reise_frame, text="Gesamtstrecke:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.gesamtstrecke_label = ttk.Label(reise_frame, text="0.0 km", font=("Arial", 10))
        self.gesamtstrecke_label.grid(row=0, column=5, padx=5)
        
        # Bindings für automatische Berechnung
        self.reisestrecke_var.trace("w", lambda *args: self._berechnen_strecke())
        self.anzahl_fahrten_var.trace("w", lambda *args: self._berechnen_strecke())
        
        # Ort, Datum, Unterschriften
        unterschrift_frame = ttk.Frame(footer_frame)
        unterschrift_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(unterschrift_frame, text="Ort:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.ort_var = tk.StringVar()
        ttk.Entry(unterschrift_frame, textvariable=self.ort_var, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(unterschrift_frame, text="Datum:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.datum_var = tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
        ttk.Entry(unterschrift_frame, textvariable=self.datum_var, width=15).grid(row=0, column=3, padx=5)
        
        ttk.Label(unterschrift_frame, text="Unterschrift Kunde:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.unterschrift_kunde_var = tk.StringVar()
        ttk.Entry(unterschrift_frame, textvariable=self.unterschrift_kunde_var, width=30).grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(unterschrift_frame, text="Unterschrift Bearbeiter:").grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        self.unterschrift_bearbeiter_var = tk.StringVar()
        ttk.Entry(unterschrift_frame, textvariable=self.unterschrift_bearbeiter_var, width=30).grid(row=1, column=4, padx=5, pady=5, sticky=tk.EW)
        
        unterschrift_frame.grid_columnconfigure(1, weight=1)
        
        main_frame.grid_columnconfigure(0, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Drucken (PDF)", command=self._drucken).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Abbrechen", command=self._abbrechen).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Speichern", command=self._speichern).pack(side=tk.RIGHT, padx=5)
    
    def _lade_nachweis(self):
        """Lädt Nachweisdaten in die Felder"""
        if not self.nachweis:
            return
        
        self.projekt_var.set(self.nachweis.projekt)
        self.auftragsnummer_var.set(self.nachweis.auftragsnummer)
        self.bearbeiter_var.set(self.nachweis.bearbeiter)
        self.reisestrecke_var.set(str(self.nachweis.reisestrecke_km))
        self.anzahl_fahrten_var.set(str(self.nachweis.anzahl_fahrten))
        self.ort_var.set(self.nachweis.ort)
        self.datum_var.set(self.nachweis.datum.strftime("%d.%m.%Y"))
        self.unterschrift_kunde_var.set(self.nachweis.unterschrift_kunde)
        self.unterschrift_bearbeiter_var.set(self.nachweis.unterschrift_bearbeiter)
        
        # Kunde laden
        kunde = self.manager.get_kunde(self.auftrag.kunde_id)
        if kunde:
            self.kunde_var.set(kunde.get_vollstaendiger_name())
            self.kundenadresse_label.config(text=kunde.get_vollstaendige_adresse())
        
        # Zeiteinträge laden
        self._aktualisiere_zeiten_liste()
        self._berechnen_strecke()
    
    def _aktualisiere_zeiten_liste(self):
        """Aktualisiert die Zeiteinträge-Liste"""
        for item in self.zeiten_tree.get_children():
            self.zeiten_tree.delete(item)
        
        if self.nachweis:
            for ze in self.nachweis.zeiteintraege:
                start1_str = ze.startzeit_1.strftime("%H:%M") if ze.startzeit_1 else ""
                end1_str = ze.endzeit_1.strftime("%H:%M") if ze.endzeit_1 else ""
                start2_str = ze.startzeit_2.strftime("%H:%M") if ze.startzeit_2 else ""
                end2_str = ze.endzeit_2.strftime("%H:%M") if ze.endzeit_2 else ""
                
                datum_str = f"{ze.datum.strftime('%d.%m.%Y')} ({ze.get_wochentag()})"
                gesamt_str = f"{ze.berechne_gesamtzeit():.2f}"
                
                self.zeiten_tree.insert("", tk.END, iid=ze.id,
                                      values=(datum_str, ze.bearbeiter, start1_str, end1_str,
                                             start2_str, end2_str, gesamt_str, ze.taetigkeitsbeschreibung))
    
    def _zeiteintrag_hinzufuegen(self):
        """Fügt einen neuen Zeiteintrag hinzu"""
        dialog = ZeiteintragDialog(self.dialog, self.bearbeiter_var.get())
        if dialog.result and dialog.zeiteintrag:
            self.nachweis.add_zeiteintrag(dialog.zeiteintrag)
            self._aktualisiere_zeiten_liste()
    
    def _zeiteintrag_bearbeiten(self):
        """Bearbeitet einen ausgewählten Zeiteintrag"""
        selection = self.zeiten_tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Zeiteintrag aus.")
            return
        
        zeiteintrag_id = selection[0]
        zeiteintrag = next((ze for ze in self.nachweis.zeiteintraege if ze.id == zeiteintrag_id), None)
        
        if zeiteintrag:
            dialog = ZeiteintragDialog(self.dialog, self.bearbeiter_var.get(), zeiteintrag)
            if dialog.result and dialog.zeiteintrag:
                # Zeiteintrag aktualisieren
                for i, ze in enumerate(self.nachweis.zeiteintraege):
                    if ze.id == zeiteintrag_id:
                        self.nachweis.zeiteintraege[i] = dialog.zeiteintrag
                        break
                self._aktualisiere_zeiten_liste()
    
    def _zeiteintrag_loeschen(self):
        """Löscht einen ausgewählten Zeiteintrag"""
        selection = self.zeiten_tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Zeiteintrag aus.")
            return
        
        zeiteintrag_id = selection[0]
        if messagebox.askyesno("Löschen", "Möchten Sie diesen Zeiteintrag wirklich löschen?"):
            self.nachweis.remove_zeiteintrag(zeiteintrag_id)
            self._aktualisiere_zeiten_liste()
    
    def _berechnen_strecke(self):
        """Berechnet die Gesamtstrecke"""
        try:
            strecke = float(self.reisestrecke_var.get() or 0.0)
            anzahl = int(self.anzahl_fahrten_var.get() or 0)
            gesamt = strecke * anzahl
            self.gesamtstrecke_label.config(text=f"{gesamt:.2f} km")
        except ValueError:
            self.gesamtstrecke_label.config(text="0.0 km")
    
    def _speichern(self):
        """Speichert den Stundennachweis"""
        # Daten aktualisieren
        self.nachweis.projekt = self.projekt_var.get()
        self.nachweis.bearbeiter = self.bearbeiter_var.get()
        
        try:
            self.nachweis.reisestrecke_km = float(self.reisestrecke_var.get() or 0.0)
            self.nachweis.anzahl_fahrten = int(self.anzahl_fahrten_var.get() or 0)
        except ValueError:
            messagebox.showerror("Fehler", "Reisestrecke und Anzahl Fahrten müssen Zahlen sein.")
            return
        
        self.nachweis.ort = self.ort_var.get()
        
        # Datum parsen
        try:
            datum_str = self.datum_var.get().strip()
            if datum_str:
                self.nachweis.datum = datetime.strptime(datum_str, "%d.%m.%Y").date()
        except ValueError:
            messagebox.showerror("Fehler", "Ungültiges Datumsformat. Verwenden Sie TT.MM.JJJJ")
            return
        
        self.nachweis.unterschrift_kunde = self.unterschrift_kunde_var.get()
        self.nachweis.unterschrift_bearbeiter = self.unterschrift_bearbeiter_var.get()
        
        # Speichern
        if self.manager.get_stundennachweis(self.nachweis.id):
            self.manager.update_stundennachweis(self.nachweis)
        else:
            self.manager.add_stundennachweis(self.nachweis)
        
        self.result = True
        messagebox.showinfo("Erfolg", "Stundennachweis wurde gespeichert.")
    
    def _drucken(self):
        """Erstellt PDF des Stundennachweises"""
        # Zuerst speichern
        self._speichern()
        
        # PDF generieren
        try:
            from adapter.pdf_generator import PDFGenerator
            generator = PDFGenerator(self.manager)
            output_path = generator.erstelle_stundennachweis_pdf(self.nachweis)
            messagebox.showinfo("Erfolg", f"PDF wurde erstellt:\n{output_path}")
        except ImportError:
            messagebox.showerror("Fehler", "PDF-Generator konnte nicht geladen werden. Bitte installieren Sie reportlab:\npip install reportlab")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des PDFs:\n{str(e)}")
    
    def _abbrechen(self):
        """Bricht den Dialog ab"""
        self.dialog.destroy()


class ZeiteintragDialog:
    """Dialog zum Erstellen/Bearbeiten von Zeiteinträgen"""
    
    def __init__(self, parent: tk.Widget, default_bearbeiter: str = "", zeiteintrag: Zeiteintrag = None):
        self.zeiteintrag = zeiteintrag
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Zeiteintrag bearbeiten" if zeiteintrag else "Neuer Zeiteintrag")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._erstelle_ui(default_bearbeiter)
        
        if zeiteintrag:
            self._lade_zeiteintrag()
        
        self.dialog.wait_window()
    
    def _erstelle_ui(self, default_bearbeiter: str):
        """Erstellt die Benutzeroberfläche"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Datum
        ttk.Label(main_frame, text="Datum *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.datum_var = tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
        ttk.Entry(main_frame, textvariable=self.datum_var, width=20).grid(row=0, column=1, pady=5, sticky=tk.W)
        
        # Bearbeiter
        ttk.Label(main_frame, text="Bearbeiter *:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.bearbeiter_var = tk.StringVar(value=default_bearbeiter)
        ttk.Entry(main_frame, textvariable=self.bearbeiter_var, width=30).grid(row=1, column=1, pady=5, sticky=tk.EW)
        
        # Erste Zeitspanne
        ttk.Label(main_frame, text="Erste Zeitspanne:", font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        ttk.Label(main_frame, text="Startzeit 1 (HH:MM):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.start1_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.start1_var, width=15).grid(row=3, column=1, pady=5, sticky=tk.W)
        
        ttk.Label(main_frame, text="Endzeit 1 (HH:MM):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.end1_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.end1_var, width=15).grid(row=4, column=1, pady=5, sticky=tk.W)
        
        # Zweite Zeitspanne
        ttk.Label(main_frame, text="Zweite Zeitspanne:", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        ttk.Label(main_frame, text="Startzeit 2 (HH:MM):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.start2_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.start2_var, width=15).grid(row=6, column=1, pady=5, sticky=tk.W)
        
        ttk.Label(main_frame, text="Endzeit 2 (HH:MM):").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.end2_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.end2_var, width=15).grid(row=7, column=1, pady=5, sticky=tk.W)
        
        # Tätigkeitsbeschreibung
        ttk.Label(main_frame, text="Tätigkeitsbeschreibung:").grid(row=8, column=0, sticky=tk.NW, pady=5)
        self.taetigkeit_text = tk.Text(main_frame, width=40, height=6)
        self.taetigkeit_text.grid(row=8, column=1, pady=5, sticky=tk.EW)
        
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Abbrechen", command=self._abbrechen).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Speichern", command=self._speichern).pack(side=tk.RIGHT, padx=5)
    
    def _lade_zeiteintrag(self):
        """Lädt Zeiteintragsdaten in die Felder"""
        if not self.zeiteintrag:
            return
        
        self.datum_var.set(self.zeiteintrag.datum.strftime("%d.%m.%Y"))
        self.bearbeiter_var.set(self.zeiteintrag.bearbeiter)
        self.start1_var.set(self.zeiteintrag.startzeit_1.strftime("%H:%M") if self.zeiteintrag.startzeit_1 else "")
        self.end1_var.set(self.zeiteintrag.endzeit_1.strftime("%H:%M") if self.zeiteintrag.endzeit_1 else "")
        self.start2_var.set(self.zeiteintrag.startzeit_2.strftime("%H:%M") if self.zeiteintrag.startzeit_2 else "")
        self.end2_var.set(self.zeiteintrag.endzeit_2.strftime("%H:%M") if self.zeiteintrag.endzeit_2 else "")
        self.taetigkeit_text.delete("1.0", tk.END)
        self.taetigkeit_text.insert("1.0", self.zeiteintrag.taetigkeitsbeschreibung)
    
    def _parse_time(self, time_str: str) -> Optional[time]:
        """Parst eine Zeitzeichenkette im Format HH:MM"""
        if not time_str or not time_str.strip():
            return None
        
        try:
            parts = time_str.strip().split(":")
            if len(parts) == 2:
                hour = int(parts[0])
                minute = int(parts[1])
                if 0 <= hour < 24 and 0 <= minute < 60:
                    return time(hour, minute)
        except ValueError:
            pass
        
        return None
    
    def _speichern(self):
        """Speichert den Zeiteintrag"""
        # Validierung
        if not self.bearbeiter_var.get().strip():
            messagebox.showerror("Fehler", "Bearbeiter ist erforderlich.")
            return
        
        # Datum parsen
        try:
            datum_str = self.datum_var.get().strip()
            datum = datetime.strptime(datum_str, "%d.%m.%Y").date()
        except ValueError:
            messagebox.showerror("Fehler", "Ungültiges Datumsformat. Verwenden Sie TT.MM.JJJJ")
            return
        
        # Zeiten parsen
        start1 = self._parse_time(self.start1_var.get())
        end1 = self._parse_time(self.end1_var.get())
        start2 = self._parse_time(self.start2_var.get())
        end2 = self._parse_time(self.end2_var.get())
        
        # Mindestens eine Zeitspanne muss vorhanden sein
        if not (start1 and end1) and not (start2 and end2):
            messagebox.showerror("Fehler", "Mindestens eine vollständige Zeitspanne (Start- und Endzeit) ist erforderlich.")
            return
        
        # Zeiteintrag erstellen oder aktualisieren
        if self.zeiteintrag:
            self.zeiteintrag.datum = datum
            self.zeiteintrag.bearbeiter = self.bearbeiter_var.get().strip()
            self.zeiteintrag.startzeit_1 = start1
            self.zeiteintrag.endzeit_1 = end1
            self.zeiteintrag.startzeit_2 = start2
            self.zeiteintrag.endzeit_2 = end2
            self.zeiteintrag.taetigkeitsbeschreibung = self.taetigkeit_text.get("1.0", tk.END).strip()
        else:
            self.zeiteintrag = Zeiteintrag(
                datum=datum,
                bearbeiter=self.bearbeiter_var.get().strip(),
                startzeit_1=start1,
                endzeit_1=end1,
                startzeit_2=start2,
                endzeit_2=end2,
                taetigkeitsbeschreibung=self.taetigkeit_text.get("1.0", tk.END).strip()
            )
        
        self.result = True
        self.dialog.destroy()
    
    def _abbrechen(self):
        """Bricht den Dialog ab"""
        self.dialog.destroy()

