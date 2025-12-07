"""Beispiel für die Verwendung des PDF-Generators"""
import json
import sys
import os

# Pfad zum Hauptprojekt hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapter.pdf_generator import PDFGenerator
from datetime import datetime


def beispiel_rechnung_erstellen():
    """Erstellt eine Beispielrechnung als PDF"""
    
    # 1. Config laden
    with open('config/config.example.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 2. PDF Generator initialisieren
    pdf_gen = PDFGenerator(config)
    
    # 3. Beispieldaten
    kunde = {
        'kundennummer': 'K-001',
        'firma': 'Musterfirma GmbH',
        'name': 'Max Mustermann',
        'strasse': 'Musterstraße 123',
        'plz': '12345',
        'ort': 'Musterstadt'
    }
    
    rechnung = {
        'rechnungsnummer': 'RE20251207001',
        'rechnungsdatum': datetime.now().isoformat(),
        'leistungsdatum': datetime.now().isoformat(),
        'faelligkeitsdatum': datetime.now().isoformat(),
        'positionen': [
            {
                'beschreibung': 'Trockenbau Decke (20m²)',
                'menge': 20.0,
                'einheit': 'm²',
                'einzelpreis': 45.00,
                'gesamtpreis': 900.00
            },
            {
                'beschreibung': 'Spachteln und Streichen',
                'menge': 20.0,
                'einheit': 'm²',
                'einzelpreis': 25.00,
                'gesamtpreis': 500.00
            },
            {
                'beschreibung': 'Material (pauschal)',
                'menge': 1.0,
                'einheit': 'Stk',
                'einzelpreis': 350.00,
                'gesamtpreis': 350.00
            }
        ],
        'nettobetrag': 1750.00,
        'mwst_satz': 19.0,
        'mwst_betrag': 332.50,
        'bruttobetrag': 2082.50,
        'notizen': 'Zahlung innerhalb von 14 Tagen ohne Abzug.'
    }
    
    # 4. PDF erstellen
    ausgabepfad = 'beispiel_rechnung.pdf'
    
    # Optional: Logo-Pfad angeben (falls vorhanden)
    # logo_pfad = 'assets/logo.png'
    logo_pfad = None
    
    pdf_pfad = pdf_gen.rechnung_erstellen(
        rechnung=rechnung,
        kunde=kunde,
        ausgabepfad=ausgabepfad,
        logo_pfad=logo_pfad
    )
    
    print(f"✅ Rechnung erfolgreich erstellt: {pdf_pfad}")
    print(f"   Kunde: {kunde['firma']}")
    print(f"   Rechnungsnummer: {rechnung['rechnungsnummer']}")
    print(f"   Bruttobetrag: {rechnung['bruttobetrag']:.2f} €")


if __name__ == '__main__':
    beispiel_rechnung_erstellen()
