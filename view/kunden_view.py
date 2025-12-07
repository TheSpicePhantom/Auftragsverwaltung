"""
View für Kundenverwaltung
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from adapter.manager import DatenManager
from model.kunde import Kunde


class KundenView:
    """View für Kundenverwaltung"""
    
    def __init__(self, parent: tk.Widget, manager: DatenManager):
        self.parent = parent
        self.manager = manager
        
        self._erstelle_ui()
        self._lade_kunden()
    
    def _erstelle_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Toolbar
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Neuer Kunde", command=self._neuer_kunde).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Bearbeiten", command=self._bearbeite_kunde).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Löschen", command=self._loesche_kunde).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Aktualisieren", command=self._lade_kunden).pack(side=tk.LEFT, padx=2)
        
        # Suchleiste
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Suchen:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._suche_kunden())
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        # Treeview für Kundenliste
        tree_frame = ttk.Frame(self.parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(tree_frame, columns=("Name", "Firma", "Ort", "Telefon", "Email"), 
                                 show="tree headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.heading("#0", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Firma", text="Firma")
        self.tree.heading("Ort", text="Ort")
        self.tree.heading("Telefon", text="Telefon")
        self.tree.heading("Email", text="E-Mail")
        
        self.tree.column("#0", width=150)
        self.tree.column("Name", width=150)
        self.tree.column("Firma", width=200)
        self.tree.column("Ort", width=150)
        self.tree.column("Telefon", width=120)
        self.tree.column("Email", width=200)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.bind("<Double-1>", lambda e: self._bearbeite_kunde())
    
    def _lade_kunden(self):
        """Lädt Kunden in die Liste"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        kunden = self.manager.get_kunden()
        for kunde in kunden:
            name = f"{kunde.vorname} {kunde.name}".strip() if not kunde.firma else ""
            self.tree.insert("", tk.END, iid=kunde.id, text=kunde.id,
                           values=(name, kunde.firma, f"{kunde.plz} {kunde.ort}".strip(), 
                                  kunde.telefon, kunde.email))
    
    def _suche_kunden(self):
        """Filtert Kunden nach Suchbegriff"""
        suche = self.search_var.get().lower()
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            text = " ".join([str(v) for v in values]).lower()
            if suche in text or suche in self.tree.item(item, "text").lower():
                self.tree.set(item, "", "")
            else:
                self.tree.detach(item)
        
        # Wieder einfügen wenn Suche leer
        if not suche:
            self._lade_kunden()
    
    def _neuer_kunde(self):
        """Öffnet Dialog für neuen Kunden"""
        from view.kunden_dialog import KundenDialog
        dialog = KundenDialog(self.parent, self.manager)
        if dialog.result:
            self._lade_kunden()
    
    def _bearbeite_kunde(self):
        """Bearbeitet ausgewählten Kunden"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Kunden aus.")
            return
        
        kunde_id = selection[0]
        kunde = self.manager.get_kunde(kunde_id)
        if kunde:
            from view.kunden_dialog import KundenDialog
            dialog = KundenDialog(self.parent, self.manager, kunde)
            if dialog.result:
                self._lade_kunden()
    
    def _loesche_kunde(self):
        """Löscht ausgewählten Kunden"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Kunden aus.")
            return
        
        kunde_id = selection[0]
        kunde = self.manager.get_kunde(kunde_id)
        
        if kunde and messagebox.askyesno("Löschen", f"Möchten Sie den Kunden '{kunde.get_vollstaendiger_name()}' wirklich löschen?"):
            # Prüfe ob Kunde in Aufträgen verwendet wird
            auftraege = self.manager.get_auftraege_von_kunde(kunde_id)
            if auftraege:
                messagebox.showerror("Fehler", f"Kunde kann nicht gelöscht werden, da {len(auftraege)} Aufträge vorhanden sind.")
                return
            
            self.manager.delete_kunde(kunde_id)
            self._lade_kunden()


