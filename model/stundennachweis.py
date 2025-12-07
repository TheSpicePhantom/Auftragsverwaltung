"""
Model-Klasse für Stundennachweise
"""
from datetime import datetime, date, time
from typing import Optional, Dict, Any, List
from decimal import Decimal


class Zeiteintrag:
    """Repräsentiert einen Zeiteintrag in einem Stundennachweis"""
    
    def __init__(self,
                 datum: date,
                 bearbeiter: str,
                 startzeit_1: Optional[time] = None,
                 endzeit_1: Optional[time] = None,
                 startzeit_2: Optional[time] = None,
                 endzeit_2: Optional[time] = None,
                 taetigkeitsbeschreibung: str = "",
                 zeiteintrag_id: Optional[str] = None):
        self.id = zeiteintrag_id or self._generate_id()
        self.datum = datum
        self.bearbeiter = bearbeiter
        self.startzeit_1 = startzeit_1
        self.endzeit_1 = endzeit_1
        self.startzeit_2 = startzeit_2
        self.endzeit_2 = endzeit_2
        self.taetigkeitsbeschreibung = taetigkeitsbeschreibung
    
    def _generate_id(self) -> str:
        """Generiert eine eindeutige ID"""
        return f"ZE{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def berechne_gesamtzeit(self) -> float:
        """Berechnet die Gesamtzeit in Dezimalstunden"""
        gesamt_minuten = 0
        
        # Erste Zeitspanne
        if self.startzeit_1 and self.endzeit_1:
            start_minuten = self.startzeit_1.hour * 60 + self.startzeit_1.minute
            end_minuten = self.endzeit_1.hour * 60 + self.endzeit_1.minute
            if end_minuten >= start_minuten:
                gesamt_minuten += end_minuten - start_minuten
            else:  # Über Mitternacht
                gesamt_minuten += (24 * 60) - start_minuten + end_minuten
        
        # Zweite Zeitspanne
        if self.startzeit_2 and self.endzeit_2:
            start_minuten = self.startzeit_2.hour * 60 + self.startzeit_2.minute
            end_minuten = self.endzeit_2.hour * 60 + self.endzeit_2.minute
            if end_minuten >= start_minuten:
                gesamt_minuten += end_minuten - start_minuten
            else:  # Über Mitternacht
                gesamt_minuten += (24 * 60) - start_minuten + end_minuten
        
        # Konvertiere in Dezimalstunden
        return round(gesamt_minuten / 60.0, 2)
    
    def get_wochentag(self) -> str:
        """Gibt den Wochentag als String zurück"""
        wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        return wochentage[self.datum.weekday()]
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Zeiteintrag zu Dictionary"""
        return {
            "id": self.id,
            "datum": self.datum.isoformat(),
            "bearbeiter": self.bearbeiter,
            "startzeit_1": self.startzeit_1.isoformat() if self.startzeit_1 else None,
            "endzeit_1": self.endzeit_1.isoformat() if self.endzeit_1 else None,
            "startzeit_2": self.startzeit_2.isoformat() if self.startzeit_2 else None,
            "endzeit_2": self.endzeit_2.isoformat() if self.endzeit_2 else None,
            "taetigkeitsbeschreibung": self.taetigkeitsbeschreibung
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Zeiteintrag':
        """Erstellt Zeiteintrag aus Dictionary"""
        zeiteintrag = cls(
            datum=date.fromisoformat(data["datum"]),
            bearbeiter=data["bearbeiter"],
            startzeit_1=time.fromisoformat(data["startzeit_1"]) if data.get("startzeit_1") else None,
            endzeit_1=time.fromisoformat(data["endzeit_1"]) if data.get("endzeit_1") else None,
            startzeit_2=time.fromisoformat(data["startzeit_2"]) if data.get("startzeit_2") else None,
            endzeit_2=time.fromisoformat(data["endzeit_2"]) if data.get("endzeit_2") else None,
            taetigkeitsbeschreibung=data.get("taetigkeitsbeschreibung", ""),
            zeiteintrag_id=data["id"]
        )
        return zeiteintrag


class Stundennachweis:
    """Repräsentiert einen Stundennachweis"""
    
    def __init__(self,
                 auftrag_id: str,
                 position_id: str,
                 projekt: str = "",
                 kunde_id: str = "",
                 auftragsnummer: str = "",
                 bearbeiter: str = "",
                 reisestrecke_km: float = 0.0,
                 anzahl_fahrten: int = 0,
                 ort: str = "",
                 datum: Optional[date] = None,
                 unterschrift_kunde: str = "",
                 unterschrift_bearbeiter: str = "",
                 nachweis_id: Optional[str] = None,
                 erstellt_am: Optional[datetime] = None):
        self.id = nachweis_id or self._generate_id()
        self.auftrag_id = auftrag_id
        self.position_id = position_id
        self.projekt = projekt
        self.kunde_id = kunde_id
        self.auftragsnummer = auftragsnummer
        self.bearbeiter = bearbeiter
        self.reisestrecke_km = float(reisestrecke_km)
        self.anzahl_fahrten = int(anzahl_fahrten)
        self.ort = ort
        self.datum = datum or date.today()
        self.unterschrift_kunde = unterschrift_kunde
        self.unterschrift_bearbeiter = unterschrift_bearbeiter
        self.erstellt_am = erstellt_am or datetime.now()
        self.zeiteintraege: List[Zeiteintrag] = []
    
    def _generate_id(self) -> str:
        """Generiert eine eindeutige ID"""
        return f"SN{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def get_gesamtstrecke(self) -> float:
        """Berechnet die Gesamtstrecke in km"""
        return self.reisestrecke_km * self.anzahl_fahrten
    
    def get_gesamtstunden(self) -> float:
        """Berechnet die Gesamtstunden aller Zeiteinträge"""
        return sum(ze.berechne_gesamtzeit() for ze in self.zeiteintraege)
    
    def add_zeiteintrag(self, zeiteintrag: Zeiteintrag):
        """Fügt einen Zeiteintrag hinzu"""
        self.zeiteintraege.append(zeiteintrag)
    
    def remove_zeiteintrag(self, zeiteintrag_id: str):
        """Entfernt einen Zeiteintrag"""
        self.zeiteintraege = [ze for ze in self.zeiteintraege if ze.id != zeiteintrag_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Stundennachweis zu Dictionary"""
        return {
            "id": self.id,
            "auftrag_id": self.auftrag_id,
            "position_id": self.position_id,
            "projekt": self.projekt,
            "kunde_id": self.kunde_id,
            "auftragsnummer": self.auftragsnummer,
            "bearbeiter": self.bearbeiter,
            "reisestrecke_km": self.reisestrecke_km,
            "anzahl_fahrten": self.anzahl_fahrten,
            "ort": self.ort,
            "datum": self.datum.isoformat(),
            "unterschrift_kunde": self.unterschrift_kunde,
            "unterschrift_bearbeiter": self.unterschrift_bearbeiter,
            "erstellt_am": self.erstellt_am.isoformat(),
            "zeiteintraege": [ze.to_dict() for ze in self.zeiteintraege]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stundennachweis':
        """Erstellt Stundennachweis aus Dictionary"""
        nachweis = cls(
            auftrag_id=data["auftrag_id"],
            position_id=data["position_id"],
            projekt=data.get("projekt", ""),
            kunde_id=data.get("kunde_id", ""),
            auftragsnummer=data.get("auftragsnummer", ""),
            bearbeiter=data.get("bearbeiter", ""),
            reisestrecke_km=data.get("reisestrecke_km", 0.0),
            anzahl_fahrten=data.get("anzahl_fahrten", 0),
            ort=data.get("ort", ""),
            datum=date.fromisoformat(data["datum"]) if data.get("datum") else date.today(),
            unterschrift_kunde=data.get("unterschrift_kunde", ""),
            unterschrift_bearbeiter=data.get("unterschrift_bearbeiter", ""),
            nachweis_id=data["id"]
        )
        if data.get("erstellt_am"):
            nachweis.erstellt_am = datetime.fromisoformat(data["erstellt_am"])
        
        # Zeiteinträge hinzufügen
        for ze_data in data.get("zeiteintraege", []):
            nachweis.add_zeiteintrag(Zeiteintrag.from_dict(ze_data))
        
        return nachweis


