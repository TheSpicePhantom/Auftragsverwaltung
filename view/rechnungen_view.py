"""
View für Rechnungsverwaltung
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime, date
from adapter.manager import DatenManager


class RechnungenView:
    """View für Rechnungsverwaltung"""
    
    def __init__(self, parent: tk.Widget, manager: DatenManager):
        self.parent = parent
        self.manager = manager
        
        self._erstelle_ui()
        self._lade_rechnungen()
        
        # Aktualisiere Tab-Text nach Initialisierung
        self._aktualisiere_tab_text()
    
    def _erstelle_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Toolbar
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Bearbeiten", command=self._bearbeite_rechnung).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Als bezahlt markieren", command=self._markiere_bezahlt).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📄 PDF erstellen", command=self._pdf_erstellen).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Drucken/Exportieren", command=self._drucke_rechnung).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Aktualisieren", command=self._lade_rechnungen).pack(side=tk.LEFT, padx=2)
        
        # Treeview für Rechnungsliste
        tree_frame = ttk.Frame(self.parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(tree_frame, columns=("Kunde", "Auftrag", "Datum", "Fällig", "Status", "Bruttobetrag"), 
                                 show="tree headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.heading("#0", text="Rechnungsnummer")
        self.tree.heading("Kunde", text="Kunde")
        self.tree.heading("Auftrag", text="Auftrag")
        self.tree.heading("Datum", text="Rechnungsdatum")
        self.tree.heading("Fällig", text="Fälligkeitsdatum")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Bruttobetrag", text="Bruttobetrag")
        
        self.tree.column("#0", width=150)
        self.tree.column("Kunde", width=200)
        self.tree.column("Auftrag", width=150)
        self.tree.column("Datum", width=120)
        self.tree.column("Fällig", width=120)
        self.tree.column("Status", width=120)
        self.tree.column("Bruttobetrag", width=120)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Tag für überfällige Rechnungen (rot hinterlegen)
        self.tree.tag_configure("ueberfaellig", background="#ffcccc")
        
        self.tree.bind("<Double-1>", lambda e: self._bearbeite_rechnung())
        
        # Kontextmenü für Rechtsklick
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Bearbeiten", command=self._bearbeite_rechnung)
        self.context_menu.add_command(label="Als bezahlt markieren", command=self._markiere_bezahlt)
        self.context_menu.add_command(label="📄 PDF erstellen", command=self._pdf_erstellen)
        self.context_menu.add_command(label="Drucken/Exportieren", command=self._drucke_rechnung)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Löschen", command=self._loesche_rechnung, foreground="red")
        
        self.tree.bind("<Button-3>", self._zeige_kontextmenue)  # Rechtsklick
        import platform
        if platform.system() == "Darwin":  # macOS
            self.tree.bind("<Button-2>", self._zeige_kontextmenue)  # Ctrl+Click auf macOS
            self.tree.bind("<Control-1>", self._zeige_kontextmenue)
    
    def _lade_rechnungen(self):
        """Lädt Rechnungen in die Liste"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        rechnungen = self.manager.get_rechnungen()
        heute = date.today()
        
        for rechnung in rechnungen:
            kunde = self.manager.get_kunde(rechnung.kunde_id)
            kunde_name = kunde.get_vollstaendiger_name() if kunde else "Unbekannt"
            
            auftrag = self.manager.get_auftrag(rechnung.auftrag_id)
            auftrag_nr = auftrag.auftragsnummer if auftrag else "Unbekannt"
            
            # Prüfe ob Rechnung überfällig ist
            faellig_datum = rechnung.faelligkeitsdatum.date() if hasattr(rechnung.faelligkeitsdatum, 'date') else rechnung.faelligkeitsdatum
            is_ueberfaellig = faellig_datum < heute and rechnung.status != "Bezahlt"
            
            # Tags für überfällige Rechnungen
            tags = ["ueberfaellig"] if is_ueberfaellig else []
            
            self.tree.insert("", tk.END, iid=rechnung.id, text=rechnung.rechnungsnummer,
                           values=(kunde_name, auftrag_nr, rechnung.rechnungsdatum.strftime("%d.%m.%Y"),
                                  rechnung.faelligkeitsdatum.strftime("%d.%m.%Y"), rechnung.status,
                                  f"{rechnung.bruttobetrag:.2f} €"),
                           tags=tags)
        
        # Aktualisiere Tab-Text im Hauptfenster
        self._aktualisiere_tab_text()
    
    def _bearbeite_rechnung(self):
        """Bearbeitet ausgewählte Rechnung"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Rechnung aus.")
            return
        
        rechnung_id = selection[0]
        rechnung = self.manager.get_rechnung(rechnung_id)
        if rechnung:
            from view.rechnungen_dialog import RechnungenDialog
            dialog = RechnungenDialog(self.parent, self.manager, rechnung)
            if dialog.result:
                self._lade_rechnungen()
    
    def _markiere_bezahlt(self):
        """Markiert Rechnung als bezahlt"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Rechnung aus.")
            return
        
        rechnung_id = selection[0]
        rechnung = self.manager.get_rechnung(rechnung_id)
        if rechnung:
            rechnung.status = "Bezahlt"
            self.manager.update_rechnung(rechnung)
            self._lade_rechnungen()
            self._aktualisiere_tab_text()
            messagebox.showinfo("Erfolg", "Rechnung wurde als bezahlt markiert.")
    
    def _pdf_erstellen(self):
        """Erstellt PDF mit Dateidialog"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte Rechnung auswählen")
            return
        
        rechnung_id = selection[0]
        rechnung = self.manager.get_rechnung(rechnung_id)
        if not rechnung:
            messagebox.showerror("Fehler", "Rechnung nicht gefunden.")
            return
        
        kunde = self.manager.get_kunde(rechnung.kunde_id)
        if not kunde:
            messagebox.showerror("Fehler", "Kunde nicht gefunden.")
            return
        
        # Speicherort wählen
        pfad = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"Rechnung_{rechnung.rechnungsnummer}.pdf"
        )
        
        if pfad:
            try:
                from adapter.pdf_generator import PDFGenerator
                pdf_gen = PDFGenerator(self.manager.adapter.config)
                auftrag = self.manager.get_auftrag(rechnung.auftrag_id)
                auftragsnummer = auftrag.auftragsnummer if auftrag else None
                pdf_gen.rechnung_erstellen(
                    rechnung.to_dict(auftragsnummer=auftragsnummer), 
                    kunde.to_dict(), 
                    pfad
                )
                messagebox.showinfo("Erfolg", f"PDF erstellt:\n{pfad}")
            except ImportError:
                messagebox.showerror("Fehler", "PDF-Generator konnte nicht geladen werden. Bitte installieren Sie reportlab:\npip install reportlab")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Erstellen des PDFs:\n{str(e)}")
    
    def _drucke_rechnung(self):
        """Druckt/Exportiert Rechnung"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Rechnung aus.")
            return
        
        rechnung_id = selection[0]
        rechnung = self.manager.get_rechnung(rechnung_id)
        if rechnung:
            try:
                from adapter.pdf_generator import PDFGenerator
                generator = PDFGenerator(self.manager.adapter.config)
                # Verwende die neue rechnung_erstellen Methode
                kunde = self.manager.get_kunde(rechnung.kunde_id)
                if kunde:
                    # Standard-Pfad im Rechnungen-Ordner des Auftrags
                    auftrag = self.manager.get_auftrag(rechnung.auftrag_id)
                    if auftrag:
                        auftragsordner = self.manager.adapter.get_auftragsordner_pfad(auftrag.auftragsnummer)
                        if auftragsordner:
                            rechnungen_ordner = Path(auftragsordner) / "Rechnungen"
                            rechnungen_ordner.mkdir(parents=True, exist_ok=True)
                            datum_str = rechnung.rechnungsdatum.strftime("%Y%m%d")
                            dateiname = f"Rechnung_{rechnung.rechnungsnummer}_{datum_str}.pdf"
                            output_path = str(rechnungen_ordner / dateiname)
                        else:
                            # Fallback: Dateidialog
                            output_path = filedialog.asksaveasfilename(
                                defaultextension=".pdf",
                                filetypes=[("PDF", "*.pdf")],
                                initialfile=f"Rechnung_{rechnung.rechnungsnummer}.pdf"
                            )
                            if not output_path:
                                return
                    else:
                        # Fallback: Dateidialog
                        output_path = filedialog.asksaveasfilename(
                            defaultextension=".pdf",
                            filetypes=[("PDF", "*.pdf")],
                            initialfile=f"Rechnung_{rechnung.rechnungsnummer}.pdf"
                        )
                        if not output_path:
                            return
                    
                    auftrag = self.manager.get_auftrag(rechnung.auftrag_id)
                    auftragsnummer = auftrag.auftragsnummer if auftrag else None
                    generator.rechnung_erstellen(
                        rechnung.to_dict(auftragsnummer=auftragsnummer),
                        kunde.to_dict(),
                        output_path
                    )
                    messagebox.showinfo("Erfolg", f"PDF wurde erstellt:\n{output_path}")
            except ImportError:
                messagebox.showerror("Fehler", "PDF-Generator konnte nicht geladen werden. Bitte installieren Sie reportlab:\npip install reportlab")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Erstellen des PDFs:\n{str(e)}")
    
    def _zeige_kontextmenue(self, event):
        """Zeigt das Kontextmenü bei Rechtsklick"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _loesche_rechnung(self):
        """Löscht die ausgewählte Rechnung"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Rechnung aus.")
            return
        
        rechnung_id = selection[0]
        rechnung = self.manager.get_rechnung(rechnung_id)
        if rechnung:
            # Sicherheitsabfrage
            antwort = messagebox.askyesno(
                "Rechnung löschen",
                f"Möchten Sie die Rechnung {rechnung.rechnungsnummer} wirklich löschen?\n\n"
                "Diese Aktion kann nicht rückgängig gemacht werden."
            )
            if antwort:
                # Lösche zuerst die PDF-Datei, falls vorhanden
                auftrag = self.manager.get_auftrag(rechnung.auftrag_id)
                if auftrag:
                    auftragsordner = self.manager.adapter.get_auftragsordner_pfad(auftrag.auftragsnummer)
                    if auftragsordner:
                        rechnungen_ordner = Path(auftragsordner) / "Rechnungen"
                        if rechnungen_ordner.exists():
                            # Konstruiere Dateiname
                            datum_str = rechnung.rechnungsdatum.strftime("%Y%m%d")
                            dateiname = f"Rechnung_{rechnung.rechnungsnummer}_{datum_str}.pdf"
                            pdf_pfad = rechnungen_ordner / dateiname
                            
                            # Lösche PDF-Datei falls vorhanden
                            if pdf_pfad.exists():
                                try:
                                    pdf_pfad.unlink()
                                except Exception as e:
                                    # Fehler beim Löschen der PDF, aber Rechnung trotzdem löschen
                                    print(f"Warnung: PDF konnte nicht gelöscht werden: {e}")
                
                # Lösche Rechnung aus der Datenbank
                if self.manager.delete_rechnung(rechnung_id):
                    self._lade_rechnungen()
                    self._aktualisiere_tab_text()
                    messagebox.showinfo("Erfolg", "Rechnung wurde gelöscht.")
                else:
                    messagebox.showerror("Fehler", "Rechnung konnte nicht gelöscht werden.")
    
    def _aktualisiere_tab_text(self):
        """Aktualisiert den Tab-Text mit Anzahl überfälliger Rechnungen"""
        # Finde das Hauptfenster über parent
        parent = self.parent
        while parent and not hasattr(parent, 'notebook'):
            parent = parent.master
        
        if parent and hasattr(parent, 'notebook'):
            # Zähle überfällige Rechnungen
            rechnungen = self.manager.get_rechnungen()
            heute = date.today()
            ueberfaellige = [r for r in rechnungen 
                           if (r.faelligkeitsdatum.date() if hasattr(r.faelligkeitsdatum, 'date') else r.faelligkeitsdatum) < heute 
                           and r.status != "Bezahlt"]
            
            anzahl = len(ueberfaellige)
            if anzahl > 0:
                # Tab-Text mit Anzahl (visuell auffällig)
                tab_text = f"Rechnungen ⚠{anzahl}"
                # Aktualisiere Tab-Text (Index 3 für Rechnungen-Tab)
                parent.notebook.tab(3, text=tab_text)
            else:
                parent.notebook.tab(3, text="Rechnungen")


