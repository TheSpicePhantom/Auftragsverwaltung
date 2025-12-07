"""
Adapter-Klasse für Datenpersistenz (JSON)
"""
import json
import os
from typing import List, Optional, Dict, Any, TypeVar, Type
from pathlib import Path

T = TypeVar('T')


class DatenAdapter:
    """Verwaltet die Persistenz von Daten in JSON-Dateien"""
    
    def __init__(self, config_path: str = "config/config.json", manager=None):
        """Initialisiert den Datenadapter mit Konfiguration"""
        self.config_path = config_path
        self.config = self._lade_config()
        self.manager = manager  # Referenz zum Manager für Zugriff auf Aufträge
        self._erstelle_datenverzeichnis()
    
    def _lade_config(self) -> Dict[str, Any]:
        """Lädt die Konfiguration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _erstelle_datenverzeichnis(self):
        """Erstellt das Datenverzeichnis falls es nicht existiert"""
        daten_pfad = self._get_daten_pfad()
        if daten_pfad:
            Path(daten_pfad).mkdir(parents=True, exist_ok=True)
    
    def _get_daten_pfad(self) -> str:
        """Gibt den konfigurierten Datenpfad zurück"""
        daten_config = self.config.get("daten", {})
        daten_pfad = daten_config.get("daten_pfad", "")
        
        # Falls kein Pfad gesetzt, verwende Standard
        if not daten_pfad or daten_pfad.strip() == "":
            return "data"
        
        return daten_pfad
    
    def _get_datei_pfad(self, dateiname: str) -> str:
        """Gibt den vollständigen Pfad zu einer Datei zurück"""
        daten_pfad = self._get_daten_pfad()
        datei = self.config.get("daten", {}).get(dateiname, dateiname)
        
        # Falls absoluter Pfad, verwende direkt
        if os.path.isabs(datei):
            return datei
        
        # Kombiniere Datenpfad mit Dateiname
        return os.path.join(daten_pfad, datei)
    
    def _lade_datei(self, datei_pfad: str) -> List[Dict[str, Any]]:
        """Lädt Daten aus einer JSON-Datei"""
        if not os.path.exists(datei_pfad):
            return []
        
        try:
            with open(datei_pfad, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _speichere_datei(self, datei_pfad: str, daten: List[Dict[str, Any]]):
        """Speichert Daten in eine JSON-Datei"""
        os.makedirs(os.path.dirname(datei_pfad), exist_ok=True)
        with open(datei_pfad, 'w', encoding='utf-8') as f:
            json.dump(daten, f, ensure_ascii=False, indent=2)
    
    def lade_kunden(self) -> List[Dict[str, Any]]:
        """Lädt alle Kunden"""
        datei = self._get_datei_pfad("kunden_datei")
        return self._lade_datei(datei)
    
    def speichere_kunden(self, kunden: List[Dict[str, Any]]):
        """Speichert alle Kunden"""
        datei = self._get_datei_pfad("kunden_datei")
        self._speichere_datei(datei, kunden)
    
    def lade_auftraege(self) -> List[Dict[str, Any]]:
        """Lädt alle Aufträge"""
        datei = self._get_datei_pfad("auftraege_datei")
        return self._lade_datei(datei)
    
    def speichere_auftraege(self, auftraege: List[Dict[str, Any]]):
        """Speichert alle Aufträge"""
        datei = self._get_datei_pfad("auftraege_datei")
        self._speichere_datei(datei, auftraege)
    
    def lade_rechnungen(self) -> List[Dict[str, Any]]:
        """Lädt alle Rechnungen"""
        datei = self._get_datei_pfad("rechnungen_datei")
        return self._lade_datei(datei)
    
    def speichere_rechnungen(self, rechnungen: List[Dict[str, Any]]):
        """Speichert alle Rechnungen"""
        datei = self._get_datei_pfad("rechnungen_datei")
        self._speichere_datei(datei, rechnungen)
    
    def lade_stundennachweise(self) -> List[Dict[str, Any]]:
        """Lädt alle Stundennachweise aus allen Aufträgen"""
        alle_nachweise = []
        auftragsordner = self._get_alle_auftragsordner()
        for auftragsordner_pfad in auftragsordner:
            datei = Path(auftragsordner_pfad) / "stundennachweise.json"
            nachweise = self._lade_datei(str(datei))
            alle_nachweise.extend(nachweise)
        return alle_nachweise
    
    def speichere_stundennachweise(self, nachweise: List[Dict[str, Any]]):
        """Speichert Stundennachweise nach Auftrag gruppiert"""
        # Gruppiere nach auftrag_id
        nachweise_nach_auftrag = {}
        for nachweis in nachweise:
            auftrag_id = nachweis.get("auftrag_id")
            if auftrag_id:
                auftrag = self.manager.get_auftrag(auftrag_id) if hasattr(self, 'manager') else None
                if auftrag:
                    auftragsnummer = auftrag.auftragsnummer
                    if auftragsnummer not in nachweise_nach_auftrag:
                        nachweise_nach_auftrag[auftragsnummer] = []
                    nachweise_nach_auftrag[auftragsnummer].append(nachweis)
        
        # Speichere pro Auftrag
        for auftragsnummer, auftrag_nachweise in nachweise_nach_auftrag.items():
            auftragsordner = self.get_auftragsordner_pfad(auftragsnummer)
            if auftragsordner:
                datei = Path(auftragsordner) / "stundennachweise.json"
                self._speichere_datei(str(datei), auftrag_nachweise)
    
    def lade_stundennachweise_fuer_auftrag(self, auftragsnummer: str) -> List[Dict[str, Any]]:
        """Lädt Stundennachweise für einen spezifischen Auftrag"""
        auftragsordner = self.get_auftragsordner_pfad(auftragsnummer)
        if auftragsordner:
            datei = Path(auftragsordner) / "stundennachweise.json"
            return self._lade_datei(str(datei))
        return []
    
    def speichere_stundennachweise_fuer_auftrag(self, auftragsnummer: str, nachweise: List[Dict[str, Any]]):
        """Speichert Stundennachweise für einen spezifischen Auftrag"""
        auftragsordner = self.get_auftragsordner_pfad(auftragsnummer)
        if auftragsordner:
            datei = Path(auftragsordner) / "stundennachweise.json"
            self._speichere_datei(str(datei), nachweise)
    
    def lade_stuecklisten(self) -> List[Dict[str, Any]]:
        """Lädt alle Stücklisten aus allen Aufträgen"""
        alle_stuecklisten = []
        auftragsordner = self._get_alle_auftragsordner()
        for auftragsordner_pfad in auftragsordner:
            datei = Path(auftragsordner_pfad) / "stuecklisten.json"
            stuecklisten = self._lade_datei(str(datei))
            alle_stuecklisten.extend(stuecklisten)
        return alle_stuecklisten
    
    def speichere_stuecklisten(self, stuecklisten: List[Dict[str, Any]]):
        """Speichert Stücklisten nach Auftrag gruppiert"""
        # Gruppiere nach auftrag_id
        stuecklisten_nach_auftrag = {}
        for stueckliste in stuecklisten:
            auftrag_id = stueckliste.get("auftrag_id")
            if auftrag_id:
                auftrag = self.manager.get_auftrag(auftrag_id) if hasattr(self, 'manager') else None
                if auftrag:
                    auftragsnummer = auftrag.auftragsnummer
                    if auftragsnummer not in stuecklisten_nach_auftrag:
                        stuecklisten_nach_auftrag[auftragsnummer] = []
                    stuecklisten_nach_auftrag[auftragsnummer].append(stueckliste)
        
        # Speichere pro Auftrag
        for auftragsnummer, auftrag_stuecklisten in stuecklisten_nach_auftrag.items():
            auftragsordner = self.get_auftragsordner_pfad(auftragsnummer)
            if auftragsordner:
                datei = Path(auftragsordner) / "stuecklisten.json"
                self._speichere_datei(str(datei), auftrag_stuecklisten)
    
    def lade_stuecklisten_fuer_auftrag(self, auftragsnummer: str) -> List[Dict[str, Any]]:
        """Lädt Stücklisten für einen spezifischen Auftrag"""
        auftragsordner = self.get_auftragsordner_pfad(auftragsnummer)
        if auftragsordner:
            datei = Path(auftragsordner) / "stuecklisten.json"
            return self._lade_datei(str(datei))
        return []
    
    def speichere_stuecklisten_fuer_auftrag(self, auftragsnummer: str, stuecklisten: List[Dict[str, Any]]):
        """Speichert Stücklisten für einen spezifischen Auftrag"""
        auftragsordner = self.get_auftragsordner_pfad(auftragsnummer)
        if auftragsordner:
            datei = Path(auftragsordner) / "stuecklisten.json"
            self._speichere_datei(str(datei), stuecklisten)
    
    def lade_rechnungen_fuer_auftrag(self, auftragsnummer: str) -> List[Dict[str, Any]]:
        """Lädt Rechnungen für einen spezifischen Auftrag"""
        auftragsordner = self.get_auftragsordner_pfad(auftragsnummer)
        if auftragsordner:
            datei = Path(auftragsordner) / "rechnungen.json"
            return self._lade_datei(str(datei))
        return []
    
    def speichere_rechnungen_fuer_auftrag(self, auftragsnummer: str, rechnungen: List[Dict[str, Any]]):
        """Speichert Rechnungen für einen spezifischen Auftrag"""
        auftragsordner = self.get_auftragsordner_pfad(auftragsnummer)
        if auftragsordner:
            datei = Path(auftragsordner) / "rechnungen.json"
            self._speichere_datei(str(datei), rechnungen)
    
    def _get_alle_auftragsordner(self) -> List[str]:
        """Gibt alle Auftragsordner zurück"""
        from datetime import datetime
        basis_pfad = Path(self._get_daten_pfad())
        auftragsordner = []
        
        # Durchsuche alle Jahresordner
        if basis_pfad.exists():
            for jahresordner in basis_pfad.iterdir():
                if jahresordner.is_dir() and jahresordner.name.isdigit():
                    # Durchsuche alle Auftragsordner im Jahresordner
                    for auftrag_ordner in jahresordner.iterdir():
                        if auftrag_ordner.is_dir() and "-" in auftrag_ordner.name:
                            auftragsordner.append(str(auftrag_ordner))
        
        return auftragsordner
    
    def get_config(self) -> Dict[str, Any]:
        """Gibt die Konfiguration zurück"""
        return self.config
    
    def speichere_config(self, config: Dict[str, Any]):
        """Speichert die Konfiguration"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        self.config = config
    
    def setze_daten_pfad(self, pfad: str):
        """Setzt den Datenpfad und aktualisiert die Konfiguration"""
        if not os.path.exists(pfad):
            os.makedirs(pfad, exist_ok=True)
        
        self.config.setdefault("daten", {})["daten_pfad"] = pfad
        self.speichere_config(self.config)
        self._erstelle_datenverzeichnis()
    
    def get_daten_pfad(self) -> str:
        """Gibt den aktuellen Datenpfad zurück"""
        return self._get_daten_pfad()
    
    def erstelle_auftragsordnerstruktur(self, auftragsnummer: str):
        """
        Erstellt die hierarchische Ordnerstruktur für einen Auftrag
        
        Struktur:
        - YYYY/ (Jahresordner)
          - YYYY-XXXX/ (Hauptauftragsordner)
            - 01_(Beschreibung)/ (Teilaufträge/Positionen)
              - Dokumentation/
                - Fotos/
                - Skizzen/
                - Berechnungen/
              - Rechnungen/
                - Belege/
                - Kundenrechnungen/
        """
        import os
        from pathlib import Path
        
        # Extrahiere Jahr aus Auftragsnummer (Format: YYYY-XXXX)
        try:
            jahr = auftragsnummer.split("-")[0]
        except IndexError:
            # Fallback: aktuelles Jahr verwenden
            from datetime import datetime
            jahr = str(datetime.now().year)
        
        # Basis-Pfad: Datenverzeichnis
        basis_pfad = Path(self._get_daten_pfad())
        
        # Ebene 1: Jahresordner (YYYY)
        jahresordner = basis_pfad / jahr
        jahresordner.mkdir(parents=True, exist_ok=True)
        
        # Ebene 2: Hauptauftragsordner (YYYY-XXXX)
        auftragsordner = jahresordner / auftragsnummer
        auftragsordner.mkdir(parents=True, exist_ok=True)
        
        # Erstelle leere JSON-Dateien für auftragsspezifische Daten
        (auftragsordner / "stundennachweise.json").touch()
        (auftragsordner / "stuecklisten.json").touch()
        (auftragsordner / "rechnungen.json").touch()
        
        # Schreibe leere Arrays in die Dateien
        with open(auftragsordner / "stundennachweise.json", 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        with open(auftragsordner / "stuecklisten.json", 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        with open(auftragsordner / "rechnungen.json", 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        # Die Teilaufträge (Ebene 3) und deren Unterordner (Ebene 4) werden
        # erst erstellt, wenn ein Teilauftrag hinzugefügt wird
        # Die Grundstruktur ist damit angelegt
        
        return str(auftragsordner)
    
    def erstelle_teilauftrag_ordnerstruktur(self, auftragsnummer: str, positionsnummer: int, beschreibung: str):
        """
        Erstellt die Ordnerstruktur für einen Teilauftrag/Position
        
        Args:
            auftragsnummer: Die Auftragsnummer (YYYY-XXXX)
            positionsnummer: Die Positionsnummer (1, 2, 3, ...)
            beschreibung: Beschreibung des Teilauftrags
        """
        import os
        from pathlib import Path
        
        # Extrahiere Jahr aus Auftragsnummer
        try:
            jahr = auftragsnummer.split("-")[0]
        except IndexError:
            from datetime import datetime
            jahr = str(datetime.now().year)
        
        # Basis-Pfad
        basis_pfad = Path(self._get_daten_pfad())
        
        # Pfad zum Teilauftragsordner
        auftragsordner = basis_pfad / jahr / auftragsnummer
        
        # Ebene 3: Teilauftragsordner (ZZ_(Beschreibung))
        positionsnummer_str = f"{positionsnummer:02d}"
        # Bereinige Beschreibung für Dateisystem (entferne ungültige Zeichen)
        beschreibung_bereinigt = beschreibung.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_")
        teilauftrag_ordner = auftragsordner / f"{positionsnummer_str}_{beschreibung_bereinigt}"
        teilauftrag_ordner.mkdir(parents=True, exist_ok=True)
        
        # Ebene 4: Unterordner innerhalb des Teilauftrags
        dokumentation_ordner = teilauftrag_ordner / "Dokumentation"
        dokumentation_ordner.mkdir(exist_ok=True)
        (dokumentation_ordner / "Fotos").mkdir(exist_ok=True)
        (dokumentation_ordner / "Skizzen").mkdir(exist_ok=True)
        (dokumentation_ordner / "Berechnungen").mkdir(exist_ok=True)
        
        rechnungen_ordner = teilauftrag_ordner / "Rechnungen"
        rechnungen_ordner.mkdir(exist_ok=True)
        (rechnungen_ordner / "Belege").mkdir(exist_ok=True)
        (rechnungen_ordner / "Kundenrechnungen").mkdir(exist_ok=True)
        
        return str(teilauftrag_ordner)
    
    def get_auftragsordner_pfad(self, auftragsnummer: str) -> Optional[str]:
        """
        Gibt den Pfad zum Auftragsordner zurück
        
        Args:
            auftragsnummer: Die Auftragsnummer (YYYY-XXXX)
        
        Returns:
            Der vollständige Pfad zum Auftragsordner oder None, falls nicht gefunden
        """
        from datetime import datetime
        
        # Extrahiere Jahr aus Auftragsnummer
        try:
            jahr = auftragsnummer.split("-")[0]
        except IndexError:
            jahr = str(datetime.now().year)
        
        # Basis-Pfad
        basis_pfad = Path(self._get_daten_pfad())
        auftragsordner = basis_pfad / jahr / auftragsnummer
        
        if auftragsordner.exists():
            return str(auftragsordner)
        
        return None

