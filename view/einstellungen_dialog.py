"""
Dialog für Einstellungen
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from adapter.manager import DatenManager


class EinstellungenDialog:
    """Dialog für Einstellungen"""
    
    def __init__(self, parent: tk.Widget, manager: DatenManager):
        self.manager = manager
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Einstellungen")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._erstelle_ui()
        self._lade_einstellungen()
        
        self.dialog.wait_window()
    
    def _erstelle_ui(self):
        """Erstellt die Benutzeroberfläche"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Datenverzeichnis
        daten_frame = ttk.LabelFrame(main_frame, text="Datenverzeichnis", padding=10)
        daten_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(daten_frame, text="Aktueller Speicherort:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pfad_label = ttk.Label(daten_frame, text="", foreground="blue")
        self.pfad_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(daten_frame, text="Neuer Speicherort:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.neuer_pfad_var = tk.StringVar()
        pfad_entry = ttk.Entry(daten_frame, textvariable=self.neuer_pfad_var, width=50, state="readonly")
        pfad_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Button(daten_frame, text="Verzeichnis auswählen...", command=self._verzeichnis_auswaehlen).grid(row=1, column=2, padx=5, pady=5)
        
        daten_frame.grid_columnconfigure(1, weight=1)
        
        # Info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_text = ("Hinweis: Wenn Sie den Speicherort ändern, werden die vorhandenen Daten "
                    "automatisch in das neue Verzeichnis kopiert. Das alte Verzeichnis bleibt erhalten.")
        ttk.Label(info_frame, text=info_text, wraplength=550, foreground="gray").pack(anchor=tk.W)
        
        # Unternehmensdaten
        unternehmen_frame = ttk.LabelFrame(main_frame, text="Unternehmensdaten", padding=10)
        unternehmen_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(unternehmen_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.unternehmen_name_var = tk.StringVar()
        ttk.Entry(unternehmen_frame, textvariable=self.unternehmen_name_var, width=40).grid(row=0, column=1, pady=5, sticky=tk.EW)
        
        ttk.Label(unternehmen_frame, text="Straße:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.unternehmen_strasse_var = tk.StringVar()
        ttk.Entry(unternehmen_frame, textvariable=self.unternehmen_strasse_var, width=40).grid(row=1, column=1, pady=5, sticky=tk.EW)
        
        ttk.Label(unternehmen_frame, text="PLZ, Ort:").grid(row=2, column=0, sticky=tk.W, pady=5)
        plz_ort_frame = ttk.Frame(unternehmen_frame)
        plz_ort_frame.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        self.unternehmen_plz_var = tk.StringVar()
        ttk.Entry(plz_ort_frame, textvariable=self.unternehmen_plz_var, width=10).pack(side=tk.LEFT, padx=2)
        self.unternehmen_ort_var = tk.StringVar()
        ttk.Entry(plz_ort_frame, textvariable=self.unternehmen_ort_var, width=28).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(unternehmen_frame, text="Telefon:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.unternehmen_telefon_var = tk.StringVar()
        ttk.Entry(unternehmen_frame, textvariable=self.unternehmen_telefon_var, width=40).grid(row=3, column=1, pady=5, sticky=tk.EW)
        
        ttk.Label(unternehmen_frame, text="E-Mail:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.unternehmen_email_var = tk.StringVar()
        ttk.Entry(unternehmen_frame, textvariable=self.unternehmen_email_var, width=40).grid(row=4, column=1, pady=5, sticky=tk.EW)
        
        ttk.Label(unternehmen_frame, text="USt-ID:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.unternehmen_ust_id_var = tk.StringVar()
        ttk.Entry(unternehmen_frame, textvariable=self.unternehmen_ust_id_var, width=40).grid(row=5, column=1, pady=5, sticky=tk.EW)
        
        ttk.Label(unternehmen_frame, text="IBAN:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.unternehmen_iban_var = tk.StringVar()
        ttk.Entry(unternehmen_frame, textvariable=self.unternehmen_iban_var, width=40).grid(row=6, column=1, pady=5, sticky=tk.EW)
        
        ttk.Label(unternehmen_frame, text="BIC:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.unternehmen_bic_var = tk.StringVar()
        ttk.Entry(unternehmen_frame, textvariable=self.unternehmen_bic_var, width=40).grid(row=7, column=1, pady=5, sticky=tk.EW)
        
        unternehmen_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Abbrechen", command=self._abbrechen).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Speichern", command=self._speichern).pack(side=tk.RIGHT, padx=5)
    
    def _lade_einstellungen(self):
        """Lädt die aktuellen Einstellungen"""
        config = self.manager.adapter.get_config()
        
        # Datenpfad
        daten_pfad = self.manager.adapter.get_daten_pfad()
        if not daten_pfad or daten_pfad == "data":
            daten_pfad = os.path.abspath("data")
        self.pfad_label.config(text=daten_pfad)
        
        # Unternehmensdaten
        unternehmen = config.get("unternehmen", {})
        self.unternehmen_name_var.set(unternehmen.get("name", ""))
        self.unternehmen_strasse_var.set(unternehmen.get("strasse", ""))
        self.unternehmen_plz_var.set(unternehmen.get("plz", ""))
        self.unternehmen_ort_var.set(unternehmen.get("ort", ""))
        self.unternehmen_telefon_var.set(unternehmen.get("telefon", ""))
        self.unternehmen_email_var.set(unternehmen.get("email", ""))
        self.unternehmen_ust_id_var.set(unternehmen.get("ust_id", ""))
        self.unternehmen_iban_var.set(unternehmen.get("iban", ""))
        self.unternehmen_bic_var.set(unternehmen.get("bic", ""))
    
    def _verzeichnis_auswaehlen(self):
        """Öffnet Dialog zum Auswählen eines Verzeichnisses"""
        verzeichnis = filedialog.askdirectory(
            title="Datenverzeichnis auswählen",
            mustexist=False
        )
        
        if verzeichnis:
            self.neuer_pfad_var.set(verzeichnis)
    
    def _migriere_daten(self, alter_pfad: str, neuer_pfad: str) -> bool:
        """Migriert Daten vom alten zum neuen Pfad"""
        try:
            # Erstelle neues Verzeichnis
            os.makedirs(neuer_pfad, exist_ok=True)
            
            # Dateien die kopiert werden sollen
            dateien = ["kunden.json", "auftraege.json", "rechnungen.json"]
            
            for datei in dateien:
                alter_datei_pfad = os.path.join(alter_pfad, datei)
                neuer_datei_pfad = os.path.join(neuer_pfad, datei)
                
                # Nur kopieren wenn Datei existiert
                if os.path.exists(alter_datei_pfad):
                    shutil.copy2(alter_datei_pfad, neuer_datei_pfad)
            
            return True
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Migrieren der Daten:\n{str(e)}")
            return False
    
    def _speichern(self):
        """Speichert die Einstellungen"""
        config = self.manager.adapter.get_config()
        
        # Neuer Datenpfad
        neuer_pfad = self.neuer_pfad_var.get().strip()
        if neuer_pfad:
            alter_pfad = self.manager.adapter.get_daten_pfad()
            if alter_pfad == "data" or not alter_pfad:
                alter_pfad = os.path.abspath("data")
            else:
                alter_pfad = os.path.abspath(alter_pfad)
            
            neuer_pfad_abs = os.path.abspath(neuer_pfad)
            
            # Prüfe ob Pfad sich geändert hat
            if neuer_pfad_abs != alter_pfad:
                # Migriere Daten
                if messagebox.askyesno("Daten migrieren", 
                                     f"Möchten Sie die vorhandenen Daten nach\n{neuer_pfad}\nmigrieren?"):
                    if not self._migriere_daten(alter_pfad, neuer_pfad):
                        return
                
                # Setze neuen Pfad
                self.manager.adapter.setze_daten_pfad(neuer_pfad)
                # Lade Daten neu
                self.manager.lade_alle_daten()
                messagebox.showinfo("Erfolg", f"Datenverzeichnis wurde auf\n{neuer_pfad}\ngeändert.")
        
        # Unternehmensdaten speichern
        config.setdefault("unternehmen", {})
        config["unternehmen"]["name"] = self.unternehmen_name_var.get().strip()
        config["unternehmen"]["strasse"] = self.unternehmen_strasse_var.get().strip()
        config["unternehmen"]["plz"] = self.unternehmen_plz_var.get().strip()
        config["unternehmen"]["ort"] = self.unternehmen_ort_var.get().strip()
        config["unternehmen"]["telefon"] = self.unternehmen_telefon_var.get().strip()
        config["unternehmen"]["email"] = self.unternehmen_email_var.get().strip()
        config["unternehmen"]["ust_id"] = self.unternehmen_ust_id_var.get().strip()
        config["unternehmen"]["iban"] = self.unternehmen_iban_var.get().strip()
        config["unternehmen"]["bic"] = self.unternehmen_bic_var.get().strip()
        
        self.manager.adapter.speichere_config(config)
        
        self.result = True
        self.dialog.destroy()
    
    def _abbrechen(self):
        """Bricht den Dialog ab"""
        self.dialog.destroy()

