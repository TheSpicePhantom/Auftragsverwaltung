"""
Model-Klasse für Auftragsverwaltung
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal


class Position:
    """Repräsentiert eine Auftragsposition"""
    
    def __init__(self,
                 bezeichnung: str,
                 menge: float = 1.0,
                 einheit: str = "Stk",
                 einzelpreis: float = 0.0,
                 status: str = "zur Freigabe",
                 position_id: Optional[str] = None):
        self.id = position_id or self._generate_id()
        self.bezeichnung = bezeichnung
        self.menge = float(menge)
        self.einheit = einheit
        self.einzelpreis = float(einzelpreis)
        self.gesamtpreis = self.menge * self.einzelpreis
        self.status = status
    
    def _generate_id(self) -> str:
        """Generiert eine eindeutige ID"""
        return f"POS{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Position zu Dictionary"""
        return {
            "id": self.id,
            "bezeichnung": self.bezeichnung,
            "menge": self.menge,
            "einheit": self.einheit,
            "einzelpreis": self.einzelpreis,
            "gesamtpreis": self.gesamtpreis,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Position':
        """Erstellt Position aus Dictionary"""
        return cls(
            bezeichnung=data["bezeichnung"],
            menge=data.get("menge", 1.0),
            einheit=data.get("einheit", "Stk"),
            einzelpreis=data.get("einzelpreis", 0.0),
            status=data.get("status", "zur Freigabe"),
            position_id=data["id"]
        )


class Auftrag:
    """Repräsentiert einen Auftrag"""
    
    def __init__(self,
                 kunde_id: str,
                 bezeichnung: str,
                 beschreibung: str = "",
                 auftragsnummer: Optional[str] = None,
                 faellig_am: Optional[datetime] = None,
                 status: str = "Angebot",
                 mwst_satz: float = 19.0,
                 notizen: str = "",
                 auftrag_id: Optional[str] = None,
                 erstellt_am: Optional[datetime] = None):
        self.id = auftrag_id or self._generate_id()
        self.kunde_id = kunde_id
        self.auftragsnummer = auftragsnummer or self._generate_auftragsnummer()
        self.bezeichnung = bezeichnung
        self.beschreibung = beschreibung
        self.erstellt_am = erstellt_am or datetime.now()
        self.faellig_am = faellig_am
        self.status = status
        self.positionen: List[Position] = []
        self.mwst_satz = float(mwst_satz)
        self.notizen = notizen
        
        # Initialisiere Preisfelder
        self.gesamtpreis = 0.0
        self.mwst_betrag = 0.0
        self.endpreis = 0.0
        self._berechnen()
    
    def _generate_id(self) -> str:
        """Generiert eine eindeutige ID"""
        return f"A{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def _generate_auftragsnummer(self) -> str:
        """Generiert eine Auftragsnummer im Format YYYY-XXXX"""
        # Diese Methode wird überschrieben, wenn ein Manager verfügbar ist
        # Standardfall: Format YYYY-XXXX basierend auf aktuellem Jahr
        jahr = datetime.now().year
        return f"{jahr}-0001"
    
    def add_position(self, position: Position):
        """Fügt eine Position hinzu"""
        self.positionen.append(position)
        self._berechnen()
    
    def remove_position(self, position_id: str):
        """Entfernt eine Position"""
        self.positionen = [p for p in self.positionen if p.id != position_id]
        self._berechnen()
    
    def _berechnen(self):
        """Berechnet Gesamtpreise"""
        self.gesamtpreis = sum(p.gesamtpreis for p in self.positionen)
        self.mwst_betrag = self.gesamtpreis * (self.mwst_satz / 100)
        self.endpreis = self.gesamtpreis + self.mwst_betrag
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Auftrag zu Dictionary"""
        self._berechnen()
        return {
            "id": self.id,
            "kunde_id": self.kunde_id,
            "auftragsnummer": self.auftragsnummer,
            "bezeichnung": self.bezeichnung,
            "beschreibung": self.beschreibung,
            "erstellt_am": self.erstellt_am.isoformat(),
            "faellig_am": self.faellig_am.isoformat() if self.faellig_am else None,
            "status": self.status,
            "positionen": [p.to_dict() for p in self.positionen],
            "gesamtpreis": self.gesamtpreis,
            "mwst_satz": self.mwst_satz,
            "mwst_betrag": self.mwst_betrag,
            "endpreis": self.endpreis,
            "notizen": self.notizen
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Auftrag':
        """Erstellt Auftrag aus Dictionary"""
        auftrag = cls(
            kunde_id=data["kunde_id"],
            bezeichnung=data["bezeichnung"],
            beschreibung=data.get("beschreibung", ""),
            auftragsnummer=data.get("auftragsnummer"),
            faellig_am=datetime.fromisoformat(data["faellig_am"]) if data.get("faellig_am") else None,
            status=data.get("status", "Angebot"),
            mwst_satz=data.get("mwst_satz", 19.0),
            notizen=data.get("notizen", ""),
            auftrag_id=data["id"]
        )
        if data.get("erstellt_am"):
            auftrag.erstellt_am = datetime.fromisoformat(data["erstellt_am"])
        
        # Positionen hinzufügen
        for pos_data in data.get("positionen", []):
            auftrag.add_position(Position.from_dict(pos_data))
        
        # Stelle sicher, dass Preise berechnet sind (auch wenn keine Positionen vorhanden)
        # Dies stellt sicher, dass endpreis, gesamtpreis und mwst_betrag immer gesetzt sind
        auftrag._berechnen()
        
        return auftrag


