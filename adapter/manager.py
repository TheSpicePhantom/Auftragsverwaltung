"""
Manager-Klasse für zentrale Datenverwaltung
"""
from typing import List, Optional
from datetime import datetime
from adapter.datenadapter import DatenAdapter
from model.kunde import Kunde
from model.auftrag import Auftrag
from model.rechnung import Rechnung
from model.stundennachweis import Stundennachweis
from model.stueckliste import Stueckliste


class DatenManager:
    """Zentrale Verwaltung aller Daten"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Initialisiert den Datenmanager"""
        self.adapter = DatenAdapter(config_path)
        self.adapter.manager = self  # Setze Referenz für Zugriff auf Aufträge
        self._kunden: List[Kunde] = []
        self._auftraege: List[Auftrag] = []
        self._rechnungen: List[Rechnung] = []
        self._stundennachweise: List[Stundennachweis] = []
        self._stuecklisten: List[Stueckliste] = []
        self.lade_alle_daten()
    
    def lade_alle_daten(self):
        """Lädt alle Daten aus den Dateien"""
        # Kunden laden
        kunden_data = self.adapter.lade_kunden()
        self._kunden = [Kunde.from_dict(k) for k in kunden_data]
        
        # Aufträge laden
        auftraege_data = self.adapter.lade_auftraege()
        self._auftraege = [Auftrag.from_dict(a) for a in auftraege_data]
        
        # Rechnungen laden - aus allen Auftragsordnern
        self._rechnungen = []
        for auftrag in self._auftraege:
            rechnungen_data = self.adapter.lade_rechnungen_fuer_auftrag(auftrag.auftragsnummer)
            self._rechnungen.extend([Rechnung.from_dict(r) for r in rechnungen_data])
        
        # Stundennachweise laden
        nachweise_data = self.adapter.lade_stundennachweise()
        self._stundennachweise = [Stundennachweis.from_dict(n) for n in nachweise_data]
        
        # Stücklisten laden
        stuecklisten_data = self.adapter.lade_stuecklisten()
        self._stuecklisten = [Stueckliste.from_dict(s) for s in stuecklisten_data]
    
    def speichere_alle_daten(self):
        """Speichert alle Daten in die Dateien"""
        # Kunden speichern
        kunden_data = [k.to_dict() for k in self._kunden]
        self.adapter.speichere_kunden(kunden_data)
        
        # Aufträge speichern
        auftraege_data = [a.to_dict() for a in self._auftraege]
        self.adapter.speichere_auftraege(auftraege_data)
        
        # Rechnungen speichern - nach Auftrag gruppiert
        rechnungen_nach_auftrag = {}
        for rechnung in self._rechnungen:
            auftrag = self.get_auftrag(rechnung.auftrag_id)
            if auftrag:
                auftragsnummer = auftrag.auftragsnummer
                if auftragsnummer not in rechnungen_nach_auftrag:
                    rechnungen_nach_auftrag[auftragsnummer] = []
                rechnungen_nach_auftrag[auftragsnummer].append(rechnung.to_dict(auftragsnummer=auftragsnummer))
        
        # Speichere pro Auftrag
        for auftragsnummer, auftrag_rechnungen in rechnungen_nach_auftrag.items():
            self.adapter.speichere_rechnungen_fuer_auftrag(auftragsnummer, auftrag_rechnungen)
        
        # Stundennachweise speichern
        nachweise_data = [n.to_dict() for n in self._stundennachweise]
        self.adapter.speichere_stundennachweise(nachweise_data)
        
        # Stücklisten speichern
        stuecklisten_data = [s.to_dict() for s in self._stuecklisten]
        self.adapter.speichere_stuecklisten(stuecklisten_data)
    
    # Kunden-Methoden
    def get_kunden(self) -> List[Kunde]:
        """Gibt alle Kunden zurück"""
        return self._kunden
    
    def get_kunde(self, kunde_id: str) -> Optional[Kunde]:
        """Gibt einen Kunden anhand der ID zurück"""
        for kunde in self._kunden:
            if kunde.id == kunde_id:
                return kunde
        return None
    
    def add_kunde(self, kunde: Kunde) -> bool:
        """Fügt einen neuen Kunden hinzu"""
        if not any(k.id == kunde.id for k in self._kunden):
            self._kunden.append(kunde)
            self.speichere_alle_daten()
            return True
        return False
    
    def update_kunde(self, kunde: Kunde) -> bool:
        """Aktualisiert einen Kunden"""
        for i, k in enumerate(self._kunden):
            if k.id == kunde.id:
                self._kunden[i] = kunde
                self.speichere_alle_daten()
                return True
        return False
    
    def delete_kunde(self, kunde_id: str) -> bool:
        """Löscht einen Kunden"""
        for i, k in enumerate(self._kunden):
            if k.id == kunde_id:
                self._kunden.pop(i)
                self.speichere_alle_daten()
                return True
        return False
    
    # Auftrags-Methoden
    def get_auftraege(self) -> List[Auftrag]:
        """Gibt alle Aufträge zurück"""
        return self._auftraege
    
    def get_auftrag(self, auftrag_id: str) -> Optional[Auftrag]:
        """Gibt einen Auftrag anhand der ID zurück"""
        for auftrag in self._auftraege:
            if auftrag.id == auftrag_id:
                return auftrag
        return None
    
    def get_auftraege_von_kunde(self, kunde_id: str) -> List[Auftrag]:
        """Gibt alle Aufträge eines Kunden zurück"""
        return [a for a in self._auftraege if a.kunde_id == kunde_id]
    
    def generiere_naechste_auftragsnummer(self) -> str:
        """Generiert die nächste fortlaufende Auftragsnummer im Format YYYY-XXXX"""
        jahr = datetime.now().year
        jahr_str = str(jahr)
        
        # Finde alle Auftragsnummern des aktuellen Jahres
        auftragsnummern_des_jahres = []
        for auftrag in self._auftraege:
            if auftrag.auftragsnummer.startswith(jahr_str + "-"):
                try:
                    # Extrahiere die Nummer nach dem Bindestrich
                    nummer_teil = auftrag.auftragsnummer.split("-", 1)[1]
                    nummer = int(nummer_teil)
                    auftragsnummern_des_jahres.append(nummer)
                except (ValueError, IndexError):
                    continue
        
        # Finde die nächste freie Nummer
        if auftragsnummern_des_jahres:
            naechste_nummer = max(auftragsnummern_des_jahres) + 1
        else:
            naechste_nummer = 1
        
        # Formatiere als vierstellige Nummer
        return f"{jahr}-{naechste_nummer:04d}"
    
    def add_auftrag(self, auftrag: Auftrag) -> bool:
        """Fügt einen neuen Auftrag hinzu und erstellt die Ordnerstruktur"""
        if not any(a.id == auftrag.id for a in self._auftraege):
            # Generiere Auftragsnummer falls nicht vorhanden
            if not auftrag.auftragsnummer or auftrag.auftragsnummer.startswith("AUF"):
                auftrag.auftragsnummer = self.generiere_naechste_auftragsnummer()
            
            self._auftraege.append(auftrag)
            self.speichere_alle_daten()
            
            # Erstelle Ordnerstruktur
            self.adapter.erstelle_auftragsordnerstruktur(auftrag.auftragsnummer)
            
            # Erstelle Teilauftragsordner für jede Position
            for index, position in enumerate(auftrag.positionen, start=1):
                self.adapter.erstelle_teilauftrag_ordnerstruktur(
                    auftrag.auftragsnummer, 
                    index, 
                    position.bezeichnung
                )
            
            return True
        return False
    
    def update_auftrag(self, auftrag: Auftrag) -> bool:
        """Aktualisiert einen Auftrag und erstellt ggf. fehlende Teilauftragsordner"""
        for i, a in enumerate(self._auftraege):
            if a.id == auftrag.id:
                self._auftraege[i] = auftrag
                self.speichere_alle_daten()
                
                # Erstelle Teilauftragsordner für jede Position
                for index, position in enumerate(auftrag.positionen, start=1):
                    self.adapter.erstelle_teilauftrag_ordnerstruktur(
                        auftrag.auftragsnummer, 
                        index, 
                        position.bezeichnung
                    )
                
                return True
        return False
    
    def delete_auftrag(self, auftrag_id: str) -> bool:
        """Löscht einen Auftrag"""
        for i, a in enumerate(self._auftraege):
            if a.id == auftrag_id:
                self._auftraege.pop(i)
                self.speichere_alle_daten()
                return True
        return False
    
    # Rechnungs-Methoden
    def get_rechnungen(self) -> List[Rechnung]:
        """Gibt alle Rechnungen zurück"""
        return self._rechnungen
    
    def get_rechnung(self, rechnung_id: str) -> Optional[Rechnung]:
        """Gibt eine Rechnung anhand der ID zurück"""
        for rechnung in self._rechnungen:
            if rechnung.id == rechnung_id:
                return rechnung
        return None
    
    def get_rechnungen_von_kunde(self, kunde_id: str) -> List[Rechnung]:
        """Gibt alle Rechnungen eines Kunden zurück"""
        return [r for r in self._rechnungen if r.kunde_id == kunde_id]
    
    def get_rechnungen_von_auftrag(self, auftrag_id: str) -> List[Rechnung]:
        """Gibt alle Rechnungen eines Auftrags zurück"""
        return [r for r in self._rechnungen if r.auftrag_id == auftrag_id]
    
    def add_rechnung(self, rechnung: Rechnung) -> bool:
        """Fügt eine neue Rechnung hinzu"""
        if not any(r.id == rechnung.id for r in self._rechnungen):
            self._rechnungen.append(rechnung)
            # Speichere direkt im Auftragsordner
            auftrag = self.get_auftrag(rechnung.auftrag_id)
            if auftrag:
                rechnungen_data = self.adapter.lade_rechnungen_fuer_auftrag(auftrag.auftragsnummer)
                rechnungen_data.append(rechnung.to_dict(auftragsnummer=auftrag.auftragsnummer))
                self.adapter.speichere_rechnungen_fuer_auftrag(auftrag.auftragsnummer, rechnungen_data)
            else:
                self.speichere_alle_daten()
            return True
        return False
    
    def update_rechnung(self, rechnung: Rechnung) -> bool:
        """Aktualisiert eine Rechnung"""
        for i, r in enumerate(self._rechnungen):
            if r.id == rechnung.id:
                self._rechnungen[i] = rechnung
                # Speichere direkt im Auftragsordner
                auftrag = self.get_auftrag(rechnung.auftrag_id)
                if auftrag:
                    rechnungen_data = self.adapter.lade_rechnungen_fuer_auftrag(auftrag.auftragsnummer)
                    # Aktualisiere die Rechnung in der Liste
                    for j, rechnung_dict in enumerate(rechnungen_data):
                        if rechnung_dict.get("id") == rechnung.id:
                            rechnungen_data[j] = rechnung.to_dict(auftragsnummer=auftrag.auftragsnummer)
                            break
                    else:
                        rechnungen_data.append(rechnung.to_dict(auftragsnummer=auftrag.auftragsnummer))
                    self.adapter.speichere_rechnungen_fuer_auftrag(auftrag.auftragsnummer, rechnungen_data)
                else:
                    self.speichere_alle_daten()
                return True
        return False
    
    def delete_rechnung(self, rechnung_id: str) -> bool:
        """Löscht eine Rechnung"""
        for i, r in enumerate(self._rechnungen):
            if r.id == rechnung_id:
                auftrag = self.get_auftrag(r.auftrag_id)
                self._rechnungen.pop(i)
                # Entferne aus auftragsspezifischer Datei
                if auftrag:
                    rechnungen_data = self.adapter.lade_rechnungen_fuer_auftrag(auftrag.auftragsnummer)
                    rechnungen_data = [rd for rd in rechnungen_data if rd.get("id") != rechnung_id]
                    self.adapter.speichere_rechnungen_fuer_auftrag(auftrag.auftragsnummer, rechnungen_data)
                else:
                    self.speichere_alle_daten()
                return True
        return False
    
    def erstelle_rechnung_aus_auftrag(self, auftrag_id: str, zahlungsziel_tage: int = 14, stuecklisten_anhaengen: bool = True, status_pruefung: bool = True) -> Optional[Rechnung]:
        """Erstellt eine Rechnung aus einem Auftrag
        
        Args:
            auftrag_id: ID des Auftrags
            zahlungsziel_tage: Zahlungsziel in Tagen
            stuecklisten_anhaengen: Wenn True, werden Stücklisten als Positionen hinzugefügt
            status_pruefung: Wenn True, wird geprüft ob alle Positionen Status "Rechnung" haben
        
        Raises:
            ValueError: Wenn nicht alle Positionen den Status "Rechnung" haben
        """
        auftrag = self.get_auftrag(auftrag_id)
        if not auftrag:
            return None
        
        # Sicherheitsprüfung: Alle Positionen müssen Status "Rechnung" haben
        if status_pruefung and auftrag.positionen:
            positionen_nicht_bereit = []
            for index, pos in enumerate(auftrag.positionen, start=1):
                if pos.status != "Rechnung":
                    positionen_nicht_bereit.append(f"{index:02d}_{pos.bezeichnung} (Status: {pos.status})")
            
            if positionen_nicht_bereit:
                fehler_text = "Nicht alle Positionen haben den Status 'Rechnung'.\n\n"
                fehler_text += "Folgende Positionen müssen zuerst auf 'Rechnung' gesetzt werden:\n\n"
                fehler_text += "\n".join(positionen_nicht_bereit)
                fehler_text += "\n\nBitte setzen Sie alle Positionen auf 'Rechnung', bevor Sie eine Rechnung erstellen."
                raise ValueError(fehler_text)
        
        config = self.adapter.get_config()
        rechnung = Rechnung(
            auftrag_id=auftrag.id,
            kunde_id=auftrag.kunde_id,
            mwst_satz=auftrag.mwst_satz,
            zahlungsziel_tage=zahlungsziel_tage
        )
        
        # Positionen vom Auftrag übernehmen
        for pos in auftrag.positionen:
            rechnung.add_position(pos)
        
        # Stücklisten prüfen und hinzufügen
        stuecklisten = self.get_stuecklisten_fuer_auftrag(auftrag_id)
        stuecklisten_gesamtbetrag = sum(sl.get_gesamtbetrag() for sl in stuecklisten)
        
        if not stuecklisten:
            # Keine Stücklisten vorhanden - Rechnung als PAUSCHAL markieren
            rechnung.pauschal = True
            # Notizen erweitern um Hinweis
            if rechnung.notizen:
                rechnung.notizen += "\n\n"
            rechnung.notizen += "PAUSCHAL - Materialkosten sind bereits in den Positionen enthalten."
        elif stuecklisten_anhaengen and stuecklisten:
            # Stücklisten hinzufügen
            for stueckliste in stuecklisten:
                # Erstelle Position für Stückliste mit Stücklistennummer
                from model.auftrag import Position
                bezeichnung = f"Materialkosten - {stueckliste.projekt}"
                if stueckliste.stuecklisten_nummer:
                    bezeichnung += f" (Stückliste: {stueckliste.stuecklisten_nummer})"
                stueckliste_position = Position(
                    bezeichnung=bezeichnung,
                    menge=1.0,
                    einheit="Stk",
                    einzelpreis=stueckliste.get_gesamtbetrag()
                )
                rechnung.add_position(stueckliste_position)
            
            # 30% Aufschlag auf Stücklistenwert hinzufügen
            aufschlag_betrag = stuecklisten_gesamtbetrag * 0.30
            if aufschlag_betrag > 0:
                from model.auftrag import Position
                aufschlag_position = Position(
                    bezeichnung="Materialaufschlag (30%)",
                    menge=1.0,
                    einheit="Stk",
                    einzelpreis=aufschlag_betrag
                )
                rechnung.add_position(aufschlag_position)
        
        # Rechnung hinzufügen (wird automatisch im Auftragsordner gespeichert)
        self.add_rechnung(rechnung)
        return rechnung
    
    # Stundennachweis-Methoden
    def get_stundennachweise(self) -> List[Stundennachweis]:
        """Gibt alle Stundennachweise zurück"""
        return self._stundennachweise
    
    def get_stundennachweis(self, nachweis_id: str) -> Optional[Stundennachweis]:
        """Gibt einen Stundennachweis anhand der ID zurück"""
        for nachweis in self._stundennachweise:
            if nachweis.id == nachweis_id:
                return nachweis
        return None
    
    def get_stundennachweis_fuer_position(self, auftrag_id: str, position_id: str) -> Optional[Stundennachweis]:
        """Gibt den Stundennachweis für eine bestimmte Position zurück"""
        for nachweis in self._stundennachweise:
            if nachweis.auftrag_id == auftrag_id and nachweis.position_id == position_id:
                return nachweis
        return None
    
    def add_stundennachweis(self, nachweis: Stundennachweis) -> bool:
        """Fügt einen neuen Stundennachweis hinzu"""
        if not any(n.id == nachweis.id for n in self._stundennachweise):
            self._stundennachweise.append(nachweis)
            # Speichere direkt im Auftragsordner
            auftrag = self.get_auftrag(nachweis.auftrag_id)
            if auftrag:
                nachweise_data = self.adapter.lade_stundennachweise_fuer_auftrag(auftrag.auftragsnummer)
                nachweise_data.append(nachweis.to_dict())
                self.adapter.speichere_stundennachweise_fuer_auftrag(auftrag.auftragsnummer, nachweise_data)
            else:
                self.speichere_alle_daten()
            return True
        return False
    
    def update_stundennachweis(self, nachweis: Stundennachweis) -> bool:
        """Aktualisiert einen Stundennachweis"""
        for i, n in enumerate(self._stundennachweise):
            if n.id == nachweis.id:
                self._stundennachweise[i] = nachweis
                # Speichere direkt im Auftragsordner
                auftrag = self.get_auftrag(nachweis.auftrag_id)
                if auftrag:
                    nachweise_data = self.adapter.lade_stundennachweise_fuer_auftrag(auftrag.auftragsnummer)
                    # Aktualisiere den Nachweis in der Liste
                    for j, nachweis_dict in enumerate(nachweise_data):
                        if nachweis_dict.get("id") == nachweis.id:
                            nachweise_data[j] = nachweis.to_dict()
                            break
                    else:
                        nachweise_data.append(nachweis.to_dict())
                    self.adapter.speichere_stundennachweise_fuer_auftrag(auftrag.auftragsnummer, nachweise_data)
                else:
                    self.speichere_alle_daten()
                return True
        return False
    
    def delete_stundennachweis(self, nachweis_id: str) -> bool:
        """Löscht einen Stundennachweis"""
        for i, n in enumerate(self._stundennachweise):
            if n.id == nachweis_id:
                auftrag = self.get_auftrag(n.auftrag_id)
                self._stundennachweise.pop(i)
                # Entferne aus auftragsspezifischer Datei
                if auftrag:
                    nachweise_data = self.adapter.lade_stundennachweise_fuer_auftrag(auftrag.auftragsnummer)
                    nachweise_data = [nd for nd in nachweise_data if nd.get("id") != nachweis_id]
                    self.adapter.speichere_stundennachweise_fuer_auftrag(auftrag.auftragsnummer, nachweise_data)
                else:
                    self.speichere_alle_daten()
                return True
        return False
    
    # Stücklisten-Methoden
    def get_stuecklisten(self) -> List[Stueckliste]:
        """Gibt alle Stücklisten zurück"""
        return self._stuecklisten
    
    def get_stueckliste(self, stueckliste_id: str) -> Optional[Stueckliste]:
        """Gibt eine Stückliste anhand der ID zurück"""
        for stueckliste in self._stuecklisten:
            if stueckliste.id == stueckliste_id:
                return stueckliste
        return None
    
    def get_stueckliste_fuer_position(self, auftrag_id: str, position_id: str) -> Optional[Stueckliste]:
        """Gibt die Stückliste für eine bestimmte Position zurück"""
        for stueckliste in self._stuecklisten:
            if stueckliste.auftrag_id == auftrag_id and stueckliste.position_id == position_id:
                return stueckliste
        return None
    
    def get_stuecklisten_fuer_auftrag(self, auftrag_id: str) -> List[Stueckliste]:
        """Gibt alle Stücklisten für einen Auftrag zurück"""
        return [s for s in self._stuecklisten if s.auftrag_id == auftrag_id]
    
    def add_stueckliste(self, stueckliste: Stueckliste) -> bool:
        """Fügt eine neue Stückliste hinzu"""
        if not any(s.id == stueckliste.id for s in self._stuecklisten):
            self._stuecklisten.append(stueckliste)
            # Speichere direkt im Auftragsordner
            auftrag = self.get_auftrag(stueckliste.auftrag_id)
            if auftrag:
                stuecklisten_data = self.adapter.lade_stuecklisten_fuer_auftrag(auftrag.auftragsnummer)
                stuecklisten_data.append(stueckliste.to_dict())
                self.adapter.speichere_stuecklisten_fuer_auftrag(auftrag.auftragsnummer, stuecklisten_data)
            else:
                self.speichere_alle_daten()
            return True
        return False
    
    def update_stueckliste(self, stueckliste: Stueckliste) -> bool:
        """Aktualisiert eine Stückliste"""
        for i, s in enumerate(self._stuecklisten):
            if s.id == stueckliste.id:
                self._stuecklisten[i] = stueckliste
                # Speichere direkt im Auftragsordner
                auftrag = self.get_auftrag(stueckliste.auftrag_id)
                if auftrag:
                    stuecklisten_data = self.adapter.lade_stuecklisten_fuer_auftrag(auftrag.auftragsnummer)
                    # Aktualisiere die Stückliste in der Liste
                    for j, stueckliste_dict in enumerate(stuecklisten_data):
                        if stueckliste_dict.get("id") == stueckliste.id:
                            stuecklisten_data[j] = stueckliste.to_dict()
                            break
                    else:
                        stuecklisten_data.append(stueckliste.to_dict())
                    self.adapter.speichere_stuecklisten_fuer_auftrag(auftrag.auftragsnummer, stuecklisten_data)
                else:
                    self.speichere_alle_daten()
                return True
        return False
    
    def delete_stueckliste(self, stueckliste_id: str) -> bool:
        """Löscht eine Stückliste"""
        for i, s in enumerate(self._stuecklisten):
            if s.id == stueckliste_id:
                auftrag = self.get_auftrag(s.auftrag_id)
                self._stuecklisten.pop(i)
                # Entferne aus auftragsspezifischer Datei
                if auftrag:
                    stuecklisten_data = self.adapter.lade_stuecklisten_fuer_auftrag(auftrag.auftragsnummer)
                    stuecklisten_data = [sd for sd in stuecklisten_data if sd.get("id") != stueckliste_id]
                    self.adapter.speichere_stuecklisten_fuer_auftrag(auftrag.auftragsnummer, stuecklisten_data)
                else:
                    self.speichere_alle_daten()
                return True
        return False


