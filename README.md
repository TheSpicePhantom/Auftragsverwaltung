# Auftragsverwaltung - R. W. Kiermeier Bau- & Servicedienstleistung

Eine vollständige Auftragsverwaltung für Einzelunternehmen mit Kundenverwaltung, Auftragsverwaltung und Rechnungserstellung.

## Architektur

Das Projekt folgt dem **MVA-Prinzip** (Model, View, Adapter):

### Model
- `model/kunde.py` - Kundenmodell
- `model/auftrag.py` - Auftragsmodell mit Positionen
- `model/rechnung.py` - Rechnungsmodell

### View
- `view/hauptfenster.py` - Hauptfenster mit Tab-Navigation
- `view/kunden_view.py` - Kundenverwaltung
- `view/auftraege_view.py` - Auftragsverwaltung
- `view/rechnungen_view.py` - Rechnungsverwaltung
- `view/kunden_dialog.py` - Dialog für Kundenbearbeitung
- `view/auftraege_dialog.py` - Dialog für Auftragsbearbeitung
- `view/rechnungen_dialog.py` - Dialog für Rechnungsbearbeitung
- `view/position_dialog.py` - Dialog für Positionen

### Adapter
- `adapter/datenadapter.py` - JSON-Datenpersistenz
- `adapter/manager.py` - Zentrale Datenverwaltung

## Datenstruktur

### Konfiguration
- `config/config.json` - Unternehmensdaten, Einstellungen
- `config/data_model.json` - Datenmodell-Definition

### Daten
- `data/kunden.json` - Kundendaten
- `data/auftraege.json` - Auftragsdaten
- `data/rechnungen.json` - Rechnungsdaten

## Installation

1. Python 3.x muss installiert sein
2. Keine zusätzlichen Abhängigkeiten erforderlich (verwendet nur Standardbibliothek)

## Verwendung

```bash
python main.py
```

### Speicherort auswählen

1. Öffnen Sie die Anwendung
2. Gehen Sie zu **Datei → Einstellungen**
3. Klicken Sie auf **"Verzeichnis auswählen..."** im Bereich "Datenverzeichnis"
4. Wählen Sie Ihr gewünschtes Verzeichnis (z.B. USB-Stick)
5. Bestätigen Sie die Datenmigration, falls vorhandene Daten vorhanden sind
6. Klicken Sie auf **"Speichern"**

Die Daten werden nun im ausgewählten Verzeichnis gespeichert. Beim nächsten Start der Anwendung wird automatisch der zuletzt gewählte Speicherort verwendet.

## Features

### Kundenverwaltung
- Kunden anlegen, bearbeiten und löschen
- Suche nach Kunden
- Vollständige Kontaktdaten und Adressen
- USt-ID-Verwaltung

### Auftragsverwaltung
- Aufträge mit mehreren Positionen
- Statusverwaltung (Angebot, Bestätigt, In Bearbeitung, etc.)
- Automatische Preisberechnung mit MwSt.
- Verknüpfung mit Kunden

### Rechnungserstellung
- Rechnungen aus Aufträgen erstellen
- Automatische Übernahme von Positionen
- Statusverwaltung (Offen, Bezahlt, etc.)
- Fälligkeitsdatum-Verwaltung

### Einstellungen
- **Auswählbarer Speicherort** - Daten können auf USB-Stick oder beliebigem Verzeichnis gespeichert werden
- Automatische Datenmigration beim Wechsel des Speicherorts
- Unternehmensdaten-Verwaltung

## Initialdaten

Die Konfigurationsdatei `config/config.json` enthält:
- Unternehmensdaten (Name, Adresse, Bankverbindung)
- Standard-MwSt-Satz (19%)
- Rechnungsnummern-Präfixe
- Status-Optionen für Aufträge
- Zahlungsarten

## Erweiterungen

Mögliche zukünftige Erweiterungen:
- PDF-Export für Rechnungen
- E-Mail-Versand von Rechnungen
- Statistiken und Berichte
- Backup-Funktionalität
- Mehrbenutzer-Support

## Lizenz

Privat - R. W. Kiermeier Bau- & Servicedienstleistung

