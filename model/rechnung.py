"""
Model-Klasse für Rechnungsverwaltung
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from model.auftrag import Position


class Rechnung:
    """Repräsentiert eine Rechnung"""
    
    def __init__(self,
                 auftrag_id: str,
                 kunde_id: str,
                 rechnungsnummer: Optional[str] = None,
                 rechnungsdatum: Optional[datetime] = None,
                 leistungsdatum: Optional[datetime] = None,
                 faelligkeitsdatum: Optional[datetime] = None,
                 status: str = "Offen",
                 zahlungsart: str = "Überweisung",
                 mwst_satz: float = 19.0,
                 zahlungsziel_tage: int = 14,
                 notizen: str = "",
                 pauschal: bool = False,
                 rechnung_id: Optional[str] = None):
        self.id = rechnung_id or self._generate_id()
        self.auftrag_id = auftrag_id
        self.kunde_id = kunde_id
        self.rechnungsnummer = rechnungsnummer or self._generate_rechnungsnummer()
        self.rechnungsdatum = rechnungsdatum or datetime.now()
        self.leistungsdatum = leistungsdatum or self.rechnungsdatum
        self.faelligkeitsdatum = faelligkeitsdatum or (self.rechnungsdatum + timedelta(days=zahlungsziel_tage))
        self.status = status
        self.zahlungsart = zahlungsart
        self.positionen: List[Position] = []
        self.mwst_satz = float(mwst_satz)
        self.notizen = notizen
        self.pauschal = pauschal
    
    def _generate_id(self) -> str:
        """Generiert eine eindeutige ID"""
        return f"R{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def _generate_rechnungsnummer(self) -> str:
        """Generiert eine Rechnungsnummer"""
        return f"RE{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def add_position(self, position: Position):
        """Fügt eine Position hinzu"""
        self.positionen.append(position)
        self._berechnen()
    
    def remove_position(self, position_id: str):
        """Entfernt eine Position"""
        self.positionen = [p for p in self.positionen if p.id != position_id]
        self._berechnen()
    
    def _berechnen(self):
        """Berechnet Rechnungsbeträge"""
        self.nettobetrag = sum(p.gesamtpreis for p in self.positionen)
        self.mwst_betrag = self.nettobetrag * (self.mwst_satz / 100)
        self.bruttobetrag = self.nettobetrag + self.mwst_betrag
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Rechnung zu Dictionary"""
        self._berechnen()
        return {
            "id": self.id,
            "rechnungsnummer": self.rechnungsnummer,
            "auftrag_id": self.auftrag_id,
            "kunde_id": self.kunde_id,
            "rechnungsdatum": self.rechnungsdatum.isoformat(),
            "leistungsdatum": self.leistungsdatum.isoformat(),
            "faelligkeitsdatum": self.faelligkeitsdatum.isoformat(),
            "status": self.status,
            "positionen": [p.to_dict() for p in self.positionen],
            "nettobetrag": self.nettobetrag,
            "mwst_satz": self.mwst_satz,
            "mwst_betrag": self.mwst_betrag,
            "bruttobetrag": self.bruttobetrag,
            "zahlungsart": self.zahlungsart,
            "notizen": self.notizen,
            "pauschal": self.pauschal
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rechnung':
        """Erstellt Rechnung aus Dictionary"""
        rechnung = cls(
            auftrag_id=data["auftrag_id"],
            kunde_id=data["kunde_id"],
            rechnungsnummer=data.get("rechnungsnummer"),
            rechnungsdatum=datetime.fromisoformat(data["rechnungsdatum"]) if data.get("rechnungsdatum") else None,
            leistungsdatum=datetime.fromisoformat(data["leistungsdatum"]) if data.get("leistungsdatum") else None,
            faelligkeitsdatum=datetime.fromisoformat(data["faelligkeitsdatum"]) if data.get("faelligkeitsdatum") else None,
            status=data.get("status", "Offen"),
            zahlungsart=data.get("zahlungsart", "Überweisung"),
            mwst_satz=data.get("mwst_satz", 19.0),
            notizen=data.get("notizen", ""),
            pauschal=data.get("pauschal", False),
            rechnung_id=data["id"]
        )
        
        # Positionen hinzufügen
        for pos_data in data.get("positionen", []):
            rechnung.add_position(Position.from_dict(pos_data))
        
        return rechnung


