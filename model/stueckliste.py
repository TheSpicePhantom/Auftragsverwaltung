"""
Model-Klasse für Stücklisten
"""
from datetime import datetime
from typing import Optional, Dict, Any, List


class StuecklistenEintrag:
    """Repräsentiert einen Eintrag in einer Stückliste"""
    
    def __init__(self,
                 material: str,
                 menge: float = 1.0,
                 einheit: str = "Stk",
                 einzelpreis: float = 0.0,
                 beschreibung: str = "",
                 eintrag_id: Optional[str] = None):
        self.id = eintrag_id or self._generate_id()
        self.material = material
        self.menge = float(menge)
        self.einheit = einheit
        self.einzelpreis = float(einzelpreis)
        self.beschreibung = beschreibung
        self.gesamtpreis = self.menge * self.einzelpreis
    
    def _generate_id(self) -> str:
        """Generiert eine eindeutige ID"""
        return f"SE{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def berechne_gesamtpreis(self):
        """Berechnet den Gesamtpreis neu"""
        self.gesamtpreis = self.menge * self.einzelpreis
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Eintrag zu Dictionary"""
        return {
            "id": self.id,
            "material": self.material,
            "menge": self.menge,
            "einheit": self.einheit,
            "einzelpreis": self.einzelpreis,
            "gesamtpreis": self.gesamtpreis,
            "beschreibung": self.beschreibung
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StuecklistenEintrag':
        """Erstellt Eintrag aus Dictionary"""
        eintrag = cls(
            material=data["material"],
            menge=data.get("menge", 1.0),
            einheit=data.get("einheit", "Stk"),
            einzelpreis=data.get("einzelpreis", 0.0),
            beschreibung=data.get("beschreibung", ""),
            eintrag_id=data["id"]
        )
        return eintrag


class Stueckliste:
    """Repräsentiert eine Stückliste"""
    
    def __init__(self,
                 auftrag_id: str,
                 position_id: str,
                 projekt: str = "",
                 kunde_id: str = "",
                 auftragsnummer: str = "",
                 notizen: str = "",
                 stueckliste_id: Optional[str] = None,
                 stuecklisten_nummer: Optional[str] = None,
                 erstellt_am: Optional[datetime] = None):
        self.id = stueckliste_id or self._generate_id()
        self.auftrag_id = auftrag_id
        self.position_id = position_id
        self.projekt = projekt
        self.kunde_id = kunde_id
        self.auftragsnummer = auftragsnummer
        self.notizen = notizen
        self.stuecklisten_nummer = stuecklisten_nummer or self._generate_stuecklisten_nummer()
        self.erstellt_am = erstellt_am or datetime.now()
        self.eintraege: List[StuecklistenEintrag] = []
    
    def _generate_id(self) -> str:
        """Generiert eine eindeutige ID"""
        return f"SL{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def _generate_stuecklisten_nummer(self) -> str:
        """Generiert eine Stücklistennummer im Format SLYYYYMMDDHHMMSS"""
        return f"SL{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def get_gesamtbetrag(self) -> float:
        """Berechnet den Gesamtbetrag aller Einträge"""
        return sum(eintrag.gesamtpreis for eintrag in self.eintraege)
    
    def add_eintrag(self, eintrag: StuecklistenEintrag):
        """Fügt einen Eintrag hinzu"""
        self.eintraege.append(eintrag)
    
    def remove_eintrag(self, eintrag_id: str):
        """Entfernt einen Eintrag"""
        self.eintraege = [e for e in self.eintraege if e.id != eintrag_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Stückliste zu Dictionary"""
        return {
            "id": self.id,
            "auftrag_id": self.auftrag_id,
            "position_id": self.position_id,
            "projekt": self.projekt,
            "kunde_id": self.kunde_id,
            "auftragsnummer": self.auftragsnummer,
            "notizen": self.notizen,
            "stuecklisten_nummer": self.stuecklisten_nummer,
            "erstellt_am": self.erstellt_am.isoformat(),
            "eintraege": [e.to_dict() for e in self.eintraege]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stueckliste':
        """Erstellt Stückliste aus Dictionary"""
        stueckliste = cls(
            auftrag_id=data["auftrag_id"],
            position_id=data["position_id"],
            projekt=data.get("projekt", ""),
            kunde_id=data.get("kunde_id", ""),
            auftragsnummer=data.get("auftragsnummer", ""),
            notizen=data.get("notizen", ""),
            stueckliste_id=data["id"],
            stuecklisten_nummer=data.get("stuecklisten_nummer")
        )
        if data.get("erstellt_am"):
            stueckliste.erstellt_am = datetime.fromisoformat(data["erstellt_am"])
        
        # Einträge hinzufügen
        for e_data in data.get("eintraege", []):
            stueckliste.add_eintrag(StuecklistenEintrag.from_dict(e_data))
        
        return stueckliste

