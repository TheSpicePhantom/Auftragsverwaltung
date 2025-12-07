"""
Model-Klasse für Kundenverwaltung
"""
from datetime import datetime
from typing import Optional, Dict, Any


class Kunde:
    """Repräsentiert einen Kunden"""
    
    def __init__(self, 
                 name: str,
                 vorname: str = "",
                 firma: str = "",
                 strasse: str = "",
                 plz: str = "",
                 ort: str = "",
                 telefon: str = "",
                 email: str = "",
                 ust_id: str = "",
                 notizen: str = "",
                 skonto: float = 0.0,
                 abschlag: float = 0.0,
                 rabatt: float = 0.0,
                 kunde_id: Optional[str] = None,
                 erstellt_am: Optional[datetime] = None):
        self.id = kunde_id or self._generate_id()
        self.name = name
        self.vorname = vorname
        self.firma = firma
        self.strasse = strasse
        self.plz = plz
        self.ort = ort
        self.telefon = telefon
        self.email = email
        self.ust_id = ust_id
        self.notizen = notizen
        self.skonto = float(skonto)
        self.abschlag = float(abschlag)
        self.rabatt = float(rabatt)
        self.erstellt_am = erstellt_am or datetime.now()
    
    def _generate_id(self) -> str:
        """Generiert eine eindeutige ID"""
        return f"K{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Kunde zu Dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "vorname": self.vorname,
            "firma": self.firma,
            "strasse": self.strasse,
            "plz": self.plz,
            "ort": self.ort,
            "telefon": self.telefon,
            "email": self.email,
            "ust_id": self.ust_id,
            "erstellt_am": self.erstellt_am.isoformat(),
            "notizen": self.notizen,
            "skonto": self.skonto,
            "abschlag": self.abschlag,
            "rabatt": self.rabatt
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Kunde':
        """Erstellt Kunde aus Dictionary"""
        kunde = cls(
            name=data["name"],
            vorname=data.get("vorname", ""),
            firma=data.get("firma", ""),
            strasse=data.get("strasse", ""),
            plz=data.get("plz", ""),
            ort=data.get("ort", ""),
            telefon=data.get("telefon", ""),
            email=data.get("email", ""),
            ust_id=data.get("ust_id", ""),
            notizen=data.get("notizen", ""),
            skonto=data.get("skonto", 0.0),
            abschlag=data.get("abschlag", 0.0),
            rabatt=data.get("rabatt", 0.0),
            kunde_id=data["id"]
        )
        kunde.erstellt_am = datetime.fromisoformat(data["erstellt_am"])
        return kunde
    
    def get_vollstaendiger_name(self) -> str:
        """Gibt den vollständigen Namen zurück"""
        if self.firma:
            return self.firma
        return f"{self.vorname} {self.name}".strip()
    
    def get_vollstaendige_adresse(self) -> str:
        """Gibt die vollständige Adresse zurück"""
        adresse = []
        if self.strasse:
            adresse.append(self.strasse)
        if self.plz or self.ort:
            adresse.append(f"{self.plz} {self.ort}".strip())
        return "\n".join(adresse)


