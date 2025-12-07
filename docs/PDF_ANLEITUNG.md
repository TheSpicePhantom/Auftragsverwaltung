# PDF-Rechnungserstellung

## Installation

```bash
pip install -r requirements.txt
```

## Verwendung

### 1. Einfaches Beispiel

```python
from adapter.pdf_generator import PDFGenerator
import json

# Config laden
with open('config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# PDF Generator erstellen
pdf_gen = PDFGenerator(config)

# Rechnung als PDF speichern
pdf_pfad = pdf_gen.rechnung_erstellen(
    rechnung=rechnung_dict,  # Daten aus Rechnung.to_dict()
    kunde=kunde_dict,         # Daten aus Kunde.to_dict()
    ausgabepfad='rechnungen/RE-2025-001.pdf',
    logo_pfad='assets/logo.png'  # Optional
)
```

### 2. Integration in die GUI

In der `view/rechnungen_view.py` einen "PDF erstellen" Button hinzufügen:

```python
def pdf_erstellen(self):
    """Erstellt PDF für ausgewählte Rechnung"""
    selection = self.tree.selection()
    if not selection:
        messagebox.showwarning("Warnung", "Bitte wählen Sie eine Rechnung aus")
        return
    
    rechnung_id = selection[0]
    rechnung = self.manager.get_rechnung(rechnung_id)
    kunde = self.manager.get_kunde(rechnung.kunde_id)
    
    # Speicherort auswählen
    from tkinter import filedialog
    pfad = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Dateien", "*.pdf")],
        initialfile=f"Rechnung_{rechnung.rechnungsnummer}.pdf"
    )
    
    if pfad:
        from adapter.pdf_generator import PDFGenerator
        pdf_gen = PDFGenerator(self.manager.config)
        
        pdf_gen.rechnung_erstellen(
            rechnung=rechnung.to_dict(),
            kunde=kunde.to_dict(),
            ausgabepfad=pfad,
            logo_pfad='assets/logo.png'  # Optional anpassen
        )
        
        messagebox.showinfo("Erfolg", f"PDF erstellt: {pfad}")
```

### 3. Logo hinzufügen

1. Logo als PNG oder JPG speichern (empfohlen: 500x250px)
2. Datei nach `assets/logo.png` kopieren
3. Pfad beim PDF-Erstellen angeben:

```python
pdf_gen.rechnung_erstellen(
    ...
    logo_pfad='assets/logo.png'
)
```

## Features

### ✅ Rechtliche Konformität

- **§14 UStG**: Alle Pflichtangaben enthalten
  - Vollständige Anschriften (Leistender & Empfänger)
  - Steuernummer/USt-IdNr
  - Ausstellungsdatum
  - Fortlaufende Rechnungsnummer
  - Menge und Art der Leistung
  - Zeitpunkt der Leistung
  - Entgelt und Steuerbetrag
  - Steuersatz

- **GoBD-ready**: Strukturiert für unveränderbare Archivierung

### 📝 Layout-Elemente

- Firmenlogo (optional)
- Rechnungskopf mit allen Details
- Positionstabelle mit:
  - Position
  - Beschreibung
  - Menge
  - Einheit
  - Einzelpreis
  - Gesamtpreis
- Summierung (Netto, MwSt, Brutto)
- Zahlungshinweis
- Bankverbindung
- Fußzeile mit Pflichtangaben
- Seitennummerierung

## Beispiel ausführen

```bash
python examples/pdf_example.py
```

Erstellt eine `beispiel_rechnung.pdf` im Hauptverzeichnis.

## Troubleshooting

### ReportLab Installation fehlgeschlagen

```bash
# Windows
pip install --upgrade pip
pip install reportlab

# macOS/Linux
pip3 install reportlab
```

### Logo wird nicht angezeigt

- Prüfe Dateipfad: `os.path.exists(logo_pfad)`
- Unterstützte Formate: PNG, JPG, JPEG
- Empfohlene Auflösung: 500x250px bei 150 DPI

### PDF wird nicht erstellt

- Prüfe Schreibrechte im Zielverzeichnis
- Stelle sicher, dass das Zielverzeichnis existiert
- Prüfe ob die Datei bereits geöffnet ist

## Nächste Schritte

- [ ] E-Mail-Versand implementieren (SMTP)
- [ ] Angebote als PDF
- [ ] Lieferscheine als PDF
- [ ] Mahnungen mit Mahnstufen
- [ ] Sammel-PDF für mehrere Rechnungen
