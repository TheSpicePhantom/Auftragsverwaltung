"""
View für Auftragsverwaltung
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import platform
from adapter.manager import DatenManager


class AuftraegeView:
    """View für Auftragsverwaltung"""
    
    def __init__(self, parent: tk.Widget, manager: DatenManager, hauptfenster=None):
        self.parent = parent
        self.manager = manager
        self.hauptfenster = hauptfenster
        
        self._erstelle_ui()
        self._lade_auftraege()
    
    def _erstelle_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Toolbar
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Neuer Auftrag", command=self._neuer_auftrag).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Bearbeiten", command=self._bearbeite_auftrag).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Löschen", command=self._loesche_auftrag).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Rechnung erstellen", command=self._erstelle_rechnung).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Aktualisieren", command=self._lade_auftraege).pack(side=tk.LEFT, padx=2)
        
        # Treeview für Auftragsliste
        tree_frame = ttk.Frame(self.parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(tree_frame, columns=("Info1", "Info2", "Info3", "Info4", "Info5"), 
                                 show="tree headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.heading("#0", text="Auftrag / Position")
        self.tree.heading("Info1", text="Kunde / Menge")
        self.tree.heading("Info2", text="Bezeichnung / Einheit")
        self.tree.heading("Info3", text="Status / Einzelpreis")
        self.tree.heading("Info4", text="Endpreis / Gesamtpreis")
        self.tree.heading("Info5", text="Projekt-Status")
        
        self.tree.column("#0", width=200)
        self.tree.column("Info1", width=200)
        self.tree.column("Info2", width=250)
        self.tree.column("Info3", width=150)
        self.tree.column("Info4", width=120)
        self.tree.column("Info5", width=150)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-1>", self._on_tree_click)
        
        # Status-Optionen
        self.status_optionen = ["zur Freigabe", "Freigegeben", "in Bearbeitung", "Rechnung", "Abgeschlossen"]
        
        # Kontextmenü für Rechtsklick
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="In Explorer öffnen", command=self._oeffne_in_explorer)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Rechnung erstellen", command=self._erstelle_rechnung)
        self.context_menu.add_command(label="Stundennachweis verwalten", command=self._verwalte_stundennachweis)
        self.context_menu.add_command(label="Stückliste verwalten", command=self._verwalte_stueckliste)
        
        self.tree.bind("<Button-3>", self._zeige_kontextmenue)  # Rechtsklick
        if platform.system() == "Darwin":  # macOS
            self.tree.bind("<Button-2>", self._zeige_kontextmenue)  # Ctrl+Click auf macOS
            self.tree.bind("<Control-1>", self._zeige_kontextmenue)
    
    def _lade_auftraege(self):
        """Lädt Aufträge in die hierarchische Tree-View"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        auftraege = self.manager.get_auftraege()
        for auftrag in auftraege:
            kunde = self.manager.get_kunde(auftrag.kunde_id)
            kunde_name = kunde.get_vollstaendiger_name() if kunde else "Unbekannt"
            
            # Hauptauftrag als Root-Node einfügen
            # Text: Auftragsnummer + Bezeichnung
            auftrag_text = f"{auftrag.auftragsnummer} {auftrag.bezeichnung}"
            auftrag_node = self.tree.insert("", tk.END, iid=auftrag.id, 
                                          text=auftrag_text,
                                          values=(kunde_name, auftrag.status, 
                                                  auftrag.erstellt_am.strftime("%d.%m.%Y"),
                                                  f"{auftrag.endpreis:.2f} €", ""))
            
            # Positionen als Child-Nodes einfügen
            for index, position in enumerate(auftrag.positionen, start=1):
                # Format: 01_Bezeichnung (wie in der Ordnerstruktur)
                position_text = f"{index:02d}_{position.bezeichnung}"
                position_id = f"{auftrag.id}_pos_{position.id}"
                self.tree.insert(auftrag_node, tk.END, iid=position_id,
                               text=position_text,
                               values=(f"{position.menge:.2f}", position.einheit,
                                      f"{position.einzelpreis:.2f} €",
                                      f"{position.gesamtpreis:.2f} €",
                                      position.status))
    
    def _neuer_auftrag(self):
        """Öffnet Dialog für neuen Auftrag"""
        from view.auftraege_dialog import AuftraegeDialog
        dialog = AuftraegeDialog(self.parent, self.manager)
        if dialog.result:
            self._lade_auftraege()
    
    def _get_selected_auftrag_id(self) -> str:
        """Gibt die ID des ausgewählten Auftrags zurück (auch wenn eine Position ausgewählt ist)"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        item_id = selection[0]
        
        # Wenn es eine Position ist (Format: auftrag_id_pos_position_id)
        if "_pos_" in item_id:
            auftrag_id = item_id.split("_pos_")[0]
            return auftrag_id
        
        # Prüfe, ob es ein Auftrag ist
        auftrag = self.manager.get_auftrag(item_id)
        if auftrag:
            return item_id
        
        return None
    
    def _on_tree_click(self, event):
        """Behandelt Klick auf Tree-View - prüft ob Status-Spalte geklickt wurde"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            # Prüfe ob auf Status-Spalte (Info5) geklickt wurde und es eine Position ist
            if column == "#5" and item and "_pos_" in item:
                # Stelle sicher, dass die Position ausgewählt ist
                self.tree.selection_set(item)
                self._aendere_position_status(item, event.x_root, event.y_root)
    
    def _on_double_click(self, event):
        """Behandelt Doppelklick - öffnet Bearbeitungsdialog nur für Aufträge"""
        item = self.tree.identify_row(event.y)
        if item:
            # Prüfe, ob es ein Auftrag ist (keine Position)
            if "_pos_" not in item:
                self._bearbeite_auftrag()
    
    def _bearbeite_auftrag(self):
        """Bearbeitet ausgewählten Auftrag"""
        auftrag_id = self._get_selected_auftrag_id()
        if not auftrag_id:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Auftrag aus.")
            return
        
        auftrag = self.manager.get_auftrag(auftrag_id)
        if auftrag:
            from view.auftraege_dialog import AuftraegeDialog
            dialog = AuftraegeDialog(self.parent, self.manager, auftrag)
            if dialog.result:
                self._lade_auftraege()
    
    def _loesche_auftrag(self):
        """Löscht ausgewählten Auftrag"""
        auftrag_id = self._get_selected_auftrag_id()
        if not auftrag_id:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Auftrag aus.")
            return
        
        auftrag = self.manager.get_auftrag(auftrag_id)
        
        if auftrag and messagebox.askyesno("Löschen", f"Möchten Sie den Auftrag '{auftrag.auftragsnummer}' wirklich löschen?"):
            self.manager.delete_auftrag(auftrag_id)
            self._lade_auftraege()
    
    def _erstelle_rechnung(self):
        """Erstellt Rechnung aus Auftrag"""
        auftrag_id = self._get_selected_auftrag_id()
        if not auftrag_id:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Auftrag aus.")
            return
        
        auftrag = self.manager.get_auftrag(auftrag_id)
        
        if not auftrag:
            return
        
        if not auftrag.positionen:
            messagebox.showwarning("Keine Positionen", "Der Auftrag hat keine Positionen.")
            return
        
        # Prüfe ob Stücklisten vorhanden sind
        stuecklisten = self.manager.get_stuecklisten_fuer_auftrag(auftrag_id)
        stuecklisten_anhaengen = True
        
        if not stuecklisten:
            # Frage ob Rechnung trotzdem erstellt werden soll
            antwort = messagebox.askyesno(
                "Keine Stücklisten vorhanden",
                "Es wurden keine Stücklisten für diesen Auftrag gefunden.\n\n"
                "Möchten Sie die Rechnung trotzdem erstellen?\n\n"
                "Die Rechnung wird als PAUSCHAL markiert, da Materialkosten\n"
                "bereits in den Positionen enthalten sind."
            )
            if not antwort:
                return
            stuecklisten_anhaengen = False
        
        try:
            rechnung = self.manager.erstelle_rechnung_aus_auftrag(auftrag_id, stuecklisten_anhaengen=stuecklisten_anhaengen)
            if rechnung:
                # Erstelle PDF direkt nach Erstellung
                try:
                    from adapter.pdf_generator import PDFGenerator
                    generator = PDFGenerator(self.manager)
                    pdf_path = generator.erstelle_rechnung_pdf(rechnung)
                    
                    nachricht = f"Rechnung {rechnung.rechnungsnummer} wurde erstellt."
                    if rechnung.pauschal:
                        nachricht += "\n\nDie Rechnung wurde als PAUSCHAL markiert."
                    nachricht += f"\n\nPDF gespeichert unter:\n{pdf_path}"
                    messagebox.showinfo("Erfolg", nachricht)
                except Exception as e:
                    messagebox.showwarning(
                        "Rechnung erstellt, PDF-Fehler",
                        f"Rechnung {rechnung.rechnungsnummer} wurde erstellt, aber das PDF konnte nicht erstellt werden:\n{str(e)}"
                    )
                
                # Wechsle zu Rechnungen-Tab und aktualisiere Übersicht
                if self.hauptfenster:
                    # Aktualisiere Übersicht
                    self.hauptfenster.aktualisiere_uebersicht()
                    # Wechsle zu Rechnungen-Tab (Index 3)
                    self.hauptfenster.notebook.select(3)
                else:
                    # Fallback: Versuche über parent.master das Notebook zu finden
                    try:
                        notebook = self.parent.master
                        if notebook and hasattr(notebook, 'select'):
                            notebook.select(3)
                    except:
                        pass
        except ValueError as e:
            # Fehler bei Status-Prüfung
            messagebox.showerror("Rechnung kann nicht erstellt werden", str(e))
    
    def _zeige_kontextmenue(self, event):
        """Zeigt das Kontextmenü bei Rechtsklick"""
        # Prüfe, ob ein Eintrag ausgewählt wurde
        item = self.tree.identify_row(event.y)
        if item:
            # Stelle sicher, dass der Eintrag ausgewählt ist
            self.tree.selection_set(item)
            
            # Kontextmenü anpassen je nach Auswahl (Auftrag oder Position)
            is_position = "_pos_" in item
            
            # Menüeinträge aktivieren/deaktivieren
            try:
                # Finde den Index des "Stundennachweis verwalten" Eintrags
                menu_items = self.context_menu.index(tk.END)
                if menu_items is not None:
                    for i in range(menu_items + 1):
                        try:
                            label = self.context_menu.entryconfig(i, "label")[4]
                            if label in ["Stundennachweis verwalten", "Stückliste verwalten"]:
                                # Nur für Positionen aktivieren
                                if is_position:
                                    self.context_menu.entryconfig(i, state="normal")
                                else:
                                    self.context_menu.entryconfig(i, state="disabled")
                        except (tk.TclError, IndexError):
                            pass
            except (tk.TclError, TypeError):
                pass
            
            # Zeige Kontextmenü
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
    
    def _oeffne_in_explorer(self):
        """Öffnet den Ordner des ausgewählten Auftrags im Explorer"""
        auftrag_id = self._get_selected_auftrag_id()
        if not auftrag_id:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Auftrag aus.")
            return
        
        auftrag = self.manager.get_auftrag(auftrag_id)
        
        if not auftrag:
            return
        
        # Ermittle den Pfad zum Auftragsordner über den Adapter
        auftragsordner_pfad = self.manager.adapter.get_auftragsordner_pfad(auftrag.auftragsnummer)
        
        if not auftragsordner_pfad:
            messagebox.showwarning("Ordner nicht gefunden", 
                                 f"Der Ordner für Auftrag {auftrag.auftragsnummer} existiert noch nicht.")
            return
        
        # Öffne im Explorer
        try:
            if platform.system() == "Windows":
                os.startfile(auftragsordner_pfad)
            elif platform.system() == "Darwin":  # macOS
                os.system(f'open "{auftragsordner_pfad}"')
            else:  # Linux
                os.system(f'xdg-open "{auftragsordner_pfad}"')
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Ordners:\n{str(e)}")
    
    def _get_selected_position_id(self) -> tuple:
        """Gibt die IDs des ausgewählten Auftrags und der Position zurück (auftrag_id, position_id)"""
        selection = self.tree.selection()
        if not selection:
            return (None, None)
        
        item_id = selection[0]
        
        # Wenn es eine Position ist (Format: auftrag_id_pos_position_id)
        if "_pos_" in item_id:
            auftrag_id = item_id.split("_pos_")[0]
            position_id = item_id.split("_pos_")[1]
            return (auftrag_id, position_id)
        
        return (None, None)
    
    def _verwalte_stundennachweis(self):
        """Öffnet den Dialog zur Verwaltung des Stundennachweises"""
        auftrag_id, position_id = self._get_selected_position_id()
        if not auftrag_id or not position_id:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Teilauftrag (Position) aus.")
            return
        
        auftrag = self.manager.get_auftrag(auftrag_id)
        if not auftrag:
            messagebox.showerror("Fehler", "Auftrag nicht gefunden.")
            return
        
        from view.stundennachweis_dialog import StundennachweisDialog
        dialog = StundennachweisDialog(self.parent, self.manager, auftrag, position_id)
    
    def _verwalte_stueckliste(self):
        """Öffnet den Dialog zur Verwaltung der Stückliste"""
        auftrag_id, position_id = self._get_selected_position_id()
        if not auftrag_id or not position_id:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Teilauftrag (Position) aus.")
            return
        
        auftrag = self.manager.get_auftrag(auftrag_id)
        if not auftrag:
            messagebox.showerror("Fehler", "Auftrag nicht gefunden.")
            return
        
        from view.stueckliste_dialog import StuecklisteDialog
        dialog = StuecklisteDialog(self.parent, self.manager, auftrag, position_id)
    
    def _aendere_position_status(self, item_id: str, x: int, y: int):
        """Ändert den Status einer Position über ein Dropdown-Menü"""
        auftrag_id, position_id = self._get_selected_position_id()
        if not auftrag_id or not position_id:
            # Versuche aus item_id zu extrahieren
            if "_pos_" in item_id:
                auftrag_id = item_id.split("_pos_")[0]
                position_id = item_id.split("_pos_")[1]
            else:
                return
        
        auftrag = self.manager.get_auftrag(auftrag_id)
        if not auftrag:
            return
        
        position = next((p for p in auftrag.positionen if p.id == position_id), None)
        if not position:
            return
        
        # Erstelle Dropdown-Menü
        status_menu = tk.Menu(self.tree, tearoff=0)
        for status in self.status_optionen:
            status_menu.add_command(
                label=status,
                command=lambda s=status: self._setze_position_status(auftrag_id, position_id, s)
            )
        
        # Zeige Menü
        try:
            status_menu.tk_popup(x, y)
        finally:
            status_menu.grab_release()
    
    def _setze_position_status(self, auftrag_id: str, position_id: str, neuer_status: str):
        """Setzt den Status einer Position und speichert den Auftrag"""
        auftrag = self.manager.get_auftrag(auftrag_id)
        if not auftrag:
            return
        
        position = next((p for p in auftrag.positionen if p.id == position_id), None)
        if not position:
            return
        
        # Status aktualisieren
        position.status = neuer_status
        
        # Auftrag speichern
        self.manager.update_auftrag(auftrag)
        
        # Tree-View aktualisieren
        self._lade_auftraege()


