"""
PDF-Generator für Stundennachweise
"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from pathlib import Path
from typing import Optional
from adapter.manager import DatenManager
from model.stundennachweis import Stundennachweis
from model.stueckliste import Stueckliste
from model.rechnung import Rechnung


class PDFGenerator:
    """Generiert PDF-Dokumente für Stundennachweise"""
    
    def __init__(self, manager: DatenManager):
        self.manager = manager
        self._register_fonts()
    
    def _register_fonts(self):
        """Registriert benötigte Schriftarten"""
        # Versuche, Standard-Schriftarten zu verwenden
        # Falls spezielle Schriftarten benötigt werden, können sie hier registriert werden
        pass
    
    def erstelle_stundennachweis_pdf(self, nachweis: Stundennachweis, output_path: Optional[str] = None):
        """Erstellt ein PDF für einen Stundennachweis im Querformat"""
        # Bestimme Ausgabepfad
        if not output_path:
            # Speichere im Auftragsordner
            auftrag = self.manager.get_auftrag(nachweis.auftrag_id)
            if auftrag:
                auftragsordner = self.manager.adapter.get_auftragsordner_pfad(auftrag.auftragsnummer)
                if auftragsordner:
                    # Finde Position
                    position_index = None
                    for i, pos in enumerate(auftrag.positionen, start=1):
                        if pos.id == nachweis.position_id:
                            position_index = i
                            break
                    
                    if position_index:
                        position = next((p for p in auftrag.positionen if p.id == nachweis.position_id), None)
                        if position:
                            positionsnummer = f"{position_index:02d}"
                            beschreibung_bereinigt = position.bezeichnung.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_")
                            teilauftrag_ordner = Path(auftragsordner) / f"{positionsnummer}_{beschreibung_bereinigt}"
                            
                            # Stelle sicher, dass der Ordner existiert
                            teilauftrag_ordner.mkdir(parents=True, exist_ok=True)
                            
                            # Erstelle Dateiname
                            datum_str = nachweis.datum.strftime("%Y%m%d")
                            dateiname = f"Stundennachweis_{nachweis.auftragsnummer}_{positionsnummer}_{datum_str}.pdf"
                            output_path = str(teilauftrag_ordner / dateiname)
        
        if not output_path:
            # Fallback: Speichere im aktuellen Verzeichnis
            datum_str = nachweis.datum.strftime("%Y%m%d")
            output_path = f"Stundennachweis_{nachweis.id}_{datum_str}.pdf"
        
        # Erstelle PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Story (Inhalt) erstellen
        story = []
        styles = getSampleStyleSheet()
        
        # Kopfzeile
        header_data = self._erstelle_kopfzeile(nachweis, styles)
        story.extend(header_data)
        story.append(Spacer(1, 10*mm))
        
        # Zeiteinträge-Tabelle
        zeiten_table = self._erstelle_zeiten_tabelle(nachweis, styles)
        story.append(zeiten_table)
        story.append(Spacer(1, 10*mm))
        
        # Fußzeile
        footer_data = self._erstelle_fusszeile(nachweis, styles)
        story.extend(footer_data)
        
        # PDF erstellen
        doc.build(story)
        
        return output_path
    
    def _erstelle_kopfzeile(self, nachweis: Stundennachweis, styles) -> list:
        """Erstellt die Kopfzeile des Stundennachweises"""
        story = []
        
        # Drei-Spalten-Layout
        kunde = self.manager.get_kunde(nachweis.kunde_id)
        
        # Links: Projekt und Kunde
        left_text = f"<b>Projekt:</b><br/>{nachweis.projekt}<br/><br/><b>Kunde:</b><br/>{kunde.get_vollstaendiger_name() if kunde else ''}"
        left_para = Paragraph(left_text, styles['Normal'])
        
        # Mitte: Kundenadresse
        center_text = ""
        if kunde:
            center_text = f"<b>{kunde.get_vollstaendiger_name()}</b><br/>{kunde.get_vollstaendige_adresse()}"
        center_para = Paragraph(center_text, styles['Normal'])
        
        # Rechts: Auftragsnummer und Bearbeiter
        right_text = f"<b>Auftragsnummer:</b><br/>{nachweis.auftragsnummer}<br/><br/><b>Bearbeiter:</b><br/>{nachweis.bearbeiter}"
        right_para = Paragraph(right_text, styles['Normal'])
        
        # Tabelle für Kopfzeile
        header_table = Table(
            [[left_para, center_para, right_para]],
            colWidths=[80*mm, 100*mm, 80*mm],
            rowHeights=[40*mm]
        )
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(header_table)
        return story
    
    def _erstelle_zeiten_tabelle(self, nachweis: Stundennachweis, styles) -> Table:
        """Erstellt die Tabelle mit Zeiteinträgen"""
        # Tabellenkopf
        data = [['Datum', 'Tag + Bearbeiter', 'Startzeit', 'Endzeit', 'Startzeit', 'Endzeit', 'Gesamtzeit (h)', 'Tätigkeitsbeschreibung']]
        
        # Zeiteinträge
        for ze in nachweis.zeiteintraege:
            datum_str = ze.datum.strftime("%d.%m.%Y")
            tag_str = ze.get_wochentag()
            bearbeiter_str = ze.bearbeiter
            tag_bearbeiter = f"{tag_str}\n{bearbeiter_str}"
            
            start1_str = ze.startzeit_1.strftime("%H:%M") if ze.startzeit_1 else ""
            end1_str = ze.endzeit_1.strftime("%H:%M") if ze.endzeit_1 else ""
            start2_str = ze.startzeit_2.strftime("%H:%M") if ze.startzeit_2 else ""
            end2_str = ze.endzeit_2.strftime("%H:%M") if ze.endzeit_2 else ""
            
            gesamt_str = f"{ze.berechne_gesamtzeit():.2f}"
            
            taetigkeit = ze.taetigkeitsbeschreibung or ""
            
            data.append([
                datum_str,
                tag_bearbeiter,
                start1_str,
                end1_str,
                start2_str,
                end2_str,
                gesamt_str,
                taetigkeit
            ])
        
        # Tabelle erstellen
        table = Table(
            data,
            colWidths=[25*mm, 30*mm, 20*mm, 20*mm, 20*mm, 20*mm, 25*mm, 100*mm],
            repeatRows=1
        )
        
        # Tabellenstil
        table_style = TableStyle([
            # Kopfzeile
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Datenzeilen
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Datum links
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Tag + Bearbeiter links
            ('ALIGN', (2, 1), (6, -1), 'CENTER'),  # Zeiten zentriert
            ('ALIGN', (7, 1), (7, -1), 'LEFT'),  # Tätigkeit links
            
            # Rahmen
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ])
        
        table.setStyle(table_style)
        return table
    
    def _erstelle_fusszeile(self, nachweis: Stundennachweis, styles) -> list:
        """Erstellt die Fußzeile des Stundennachweises"""
        story = []
        
        # Reisestrecke
        gesamtstrecke = nachweis.get_gesamtstrecke()
        reise_text = f"<b>Reisestrecke:</b> {nachweis.reisestrecke_km:.2f} km × {nachweis.anzahl_fahrten} Fahrten = {gesamtstrecke:.2f} km"
        reise_para = Paragraph(reise_text, styles['Normal'])
        story.append(reise_para)
        story.append(Spacer(1, 10*mm))
        
        # Ort, Datum, Unterschriften
        ort_datum_text = f"<b>Ort:</b> {nachweis.ort} | <b>Datum:</b> {nachweis.datum.strftime('%d.%m.%Y')}"
        ort_datum_para = Paragraph(ort_datum_text, styles['Normal'])
        story.append(ort_datum_para)
        story.append(Spacer(1, 5*mm))
        
        # Unterschriften
        unterschrift_table = Table(
            [
                [f"Unterschrift Kunde:\n\n\n{nachweis.unterschrift_kunde}", 
                 f"Unterschrift Bearbeiter:\n\n\n{nachweis.unterschrift_bearbeiter}"]
            ],
            colWidths=[100*mm, 100*mm]
        )
        unterschrift_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(unterschrift_table)
        return story
    
    def erstelle_stueckliste_pdf(self, stueckliste: Stueckliste, output_path: Optional[str] = None):
        """Erstellt ein PDF für eine Stückliste"""
        # Bestimme Ausgabepfad
        if not output_path:
            # Speichere im Auftragsordner
            auftrag = self.manager.get_auftrag(stueckliste.auftrag_id)
            if auftrag:
                auftragsordner = self.manager.adapter.get_auftragsordner_pfad(auftrag.auftragsnummer)
                if auftragsordner:
                    # Finde Position
                    position_index = None
                    for i, pos in enumerate(auftrag.positionen, start=1):
                        if pos.id == stueckliste.position_id:
                            position_index = i
                            break
                    
                    if position_index:
                        position = next((p for p in auftrag.positionen if p.id == stueckliste.position_id), None)
                        if position:
                            positionsnummer = f"{position_index:02d}"
                            beschreibung_bereinigt = position.bezeichnung.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_")
                            teilauftrag_ordner = Path(auftragsordner) / f"{positionsnummer}_{beschreibung_bereinigt}"
                            
                            # Stelle sicher, dass der Ordner existiert
                            teilauftrag_ordner.mkdir(parents=True, exist_ok=True)
                            
                            # Erstelle Dateiname
                            datum_str = datetime.now().strftime("%Y%m%d")
                            dateiname = f"Stueckliste_{stueckliste.auftragsnummer}_{positionsnummer}_{datum_str}.pdf"
                            output_path = str(teilauftrag_ordner / dateiname)
        
        if not output_path:
            # Fallback: Speichere im aktuellen Verzeichnis
            datum_str = datetime.now().strftime("%Y%m%d")
            output_path = f"Stueckliste_{stueckliste.id}_{datum_str}.pdf"
        
        # Erstelle PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Story (Inhalt) erstellen
        story = []
        styles = getSampleStyleSheet()
        
        # Kopfzeile
        header_data = self._erstelle_stueckliste_kopfzeile(stueckliste, styles)
        story.extend(header_data)
        story.append(Spacer(1, 10*mm))
        
        # Einträge-Tabelle
        eintraege_table = self._erstelle_stueckliste_tabelle(stueckliste, styles)
        story.append(eintraege_table)
        story.append(Spacer(1, 10*mm))
        
        # Gesamtbetrag
        gesamt_data = self._erstelle_stueckliste_fusszeile(stueckliste, styles)
        story.extend(gesamt_data)
        
        # PDF erstellen
        doc.build(story)
        
        return output_path
    
    def _erstelle_stueckliste_kopfzeile(self, stueckliste: Stueckliste, styles) -> list:
        """Erstellt die Kopfzeile der Stückliste"""
        story = []
        
        kunde = self.manager.get_kunde(stueckliste.kunde_id)
        
        # Titel
        title = Paragraph("<b>STÜCKLISTE</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 8*mm))
        
        # Projekt, Auftragsnummer, Stücklistennummer und Kunde in separaten Zeilen
        info_text = f"<b>Projekt:</b> {stueckliste.projekt}<br/>"
        info_text += f"<b>Auftragsnummer:</b> {stueckliste.auftragsnummer}<br/>"
        if stueckliste.stuecklisten_nummer:
            info_text += f"<b>Stücklistennummer:</b> {stueckliste.stuecklisten_nummer}<br/>"
        if kunde:
            info_text += f"<b>Kunde:</b><br/>"
            info_text += f"{kunde.get_vollstaendiger_name()}<br/>"
            adresse = kunde.get_vollstaendige_adresse()
            if adresse:
                # Adresse als Block (jede Zeile separat)
                adresse_zeilen = adresse.split('\n')
                for zeile in adresse_zeilen:
                    if zeile.strip():
                        info_text += f"{zeile.strip()}<br/>"
        
        info_para = Paragraph(info_text, styles['Normal'])
        story.append(info_para)
        
        return story
    
    def _erstelle_stueckliste_tabelle(self, stueckliste: Stueckliste, styles) -> Table:
        """Erstellt die Tabelle mit Stücklisten-Einträgen"""
        # Tabellenkopf
        data = [['Material', 'Menge', 'Einheit', 'Einzelpreis (€)', 'Gesamtpreis (€)', 'Beschreibung']]
        
        # Einträge - Material als Paragraph für Word-Wrap
        for eintrag in stueckliste.eintraege:
            # Material als Paragraph für automatisches Word-Wrap
            material_para = Paragraph(eintrag.material, styles['Normal'])
            beschreibung_para = Paragraph(eintrag.beschreibung or "", styles['Normal'])
            
            data.append([
                material_para,
                f"{eintrag.menge:.2f}",
                eintrag.einheit,
                f"{eintrag.einzelpreis:.2f}",
                f"{eintrag.gesamtpreis:.2f}",
                beschreibung_para
            ])
        
        # Tabelle erstellen - Spaltenbreiten optimiert für A4 (170mm verfügbar)
        # A4 Breite: 210mm, Ränder: 20mm links + 20mm rechts = 40mm, verfügbar: 170mm
        table = Table(
            data,
            colWidths=[50*mm, 18*mm, 18*mm, 28*mm, 28*mm, 28*mm],
            repeatRows=1
        )
        
        # Tabellenstil
        table_style = TableStyle([
            # Kopfzeile
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Datenzeilen
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),  # Etwas kleinere Schrift für bessere Passform
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Material links
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),  # Menge und Einheit zentriert
            ('ALIGN', (3, 1), (4, -1), 'RIGHT'),  # Preise rechts
            ('ALIGN', (5, 1), (5, -1), 'LEFT'),  # Beschreibung links
            ('VALIGN', (0, 1), (0, -1), 'TOP'),  # Material oben ausrichten für mehrzeiligen Text
            ('VALIGN', (5, 1), (5, -1), 'TOP'),  # Beschreibung oben ausrichten für mehrzeiligen Text
            
            # Rahmen
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ])
        
        table.setStyle(table_style)
        return table
    
    def _erstelle_stueckliste_fusszeile(self, stueckliste: Stueckliste, styles) -> list:
        """Erstellt die Fußzeile der Stückliste"""
        story = []
        
        # Gesamtbetrag
        gesamtbetrag = stueckliste.get_gesamtbetrag()
        gesamt_text = f"<b>Gesamtbetrag: {gesamtbetrag:.2f} €</b>"
        gesamt_para = Paragraph(gesamt_text, styles['Normal'])
        story.append(gesamt_para)
        
        # Notizen
        if stueckliste.notizen:
            story.append(Spacer(1, 5*mm))
            notizen_text = f"<b>Notizen:</b><br/>{stueckliste.notizen}"
            notizen_para = Paragraph(notizen_text, styles['Normal'])
            story.append(notizen_para)
        
        return story
    
    def erstelle_rechnung_pdf(self, rechnung: Rechnung, output_path: Optional[str] = None):
        """Erstellt ein PDF für eine Rechnung mit optional angehängten Stücklisten"""
        # Bestimme Ausgabepfad
        if not output_path:
            auftrag = self.manager.get_auftrag(rechnung.auftrag_id)
            if auftrag:
                auftragsordner = self.manager.adapter.get_auftragsordner_pfad(auftrag.auftragsnummer)
                if auftragsordner:
                    # Erstelle "Rechnungen"-Ordner im Auftragsordner falls nicht vorhanden
                    rechnungen_ordner = Path(auftragsordner) / "Rechnungen"
                    rechnungen_ordner.mkdir(exist_ok=True)
                    
                    # Speichere im Rechnungen-Ordner
                    datum_str = rechnung.rechnungsdatum.strftime("%Y%m%d")
                    dateiname = f"Rechnung_{rechnung.rechnungsnummer}_{datum_str}.pdf"
                    output_path = str(rechnungen_ordner / dateiname)
        
        if not output_path:
            # Fallback
            datum_str = rechnung.rechnungsdatum.strftime("%Y%m%d")
            output_path = f"Rechnung_{rechnung.rechnungsnummer}_{datum_str}.pdf"
        
        # Erstelle PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Story (Inhalt) erstellen
        story = []
        styles = getSampleStyleSheet()
        
        # Rechnungskopf
        header_data = self._erstelle_rechnung_kopfzeile(rechnung, styles)
        story.extend(header_data)
        
        # PAUSCHAL-Hinweis falls vorhanden
        if rechnung.pauschal:
            story.append(Spacer(1, 5*mm))
            pauschal_text = "<b><font size=14>PAUSCHAL</font></b><br/>Materialkosten sind bereits in den Positionen enthalten."
            pauschal_para = Paragraph(pauschal_text, styles['Normal'])
            story.append(pauschal_para)
        
        story.append(Spacer(1, 10*mm))
        
        # Positionen-Tabelle
        positionen_table = self._erstelle_rechnung_positionen_tabelle(rechnung, styles)
        story.append(positionen_table)
        story.append(Spacer(1, 10*mm))
        
        # Summen
        summen_data = self._erstelle_rechnung_summen(rechnung, styles)
        story.extend(summen_data)
        
        # Stücklisten als letzte Seite(n) anhängen (nur wenn sie als Positionen enthalten sind)
        auftrag = self.manager.get_auftrag(rechnung.auftrag_id)
        if auftrag:
            # Prüfe welche Stücklisten als Positionen in der Rechnung enthalten sind
            stuecklisten_positionen = [p for p in rechnung.positionen if p.bezeichnung.startswith("Materialkosten -")]
            if stuecklisten_positionen:
                # Extrahiere Projektnamen aus den Positionen
                # Format: "Materialkosten - {Projekt} (Stückliste: {Nummer})" oder "Materialkosten - {Projekt}"
                projektnamen = []
                for p in stuecklisten_positionen:
                    # Entferne "Materialkosten - " am Anfang
                    projekt_text = p.bezeichnung.replace("Materialkosten - ", "").strip()
                    # Entferne Stücklistennummer falls vorhanden (Format: " (Stückliste: ...)")
                    if " (Stückliste:" in projekt_text:
                        projekt_text = projekt_text.split(" (Stückliste:")[0].strip()
                    projektnamen.append(projekt_text)
                
                # Lade alle Stücklisten des Auftrags
                alle_stuecklisten = self.manager.get_stuecklisten_fuer_auftrag(auftrag.id)
                # Filtere nur die Stücklisten, die auch in der Rechnung enthalten sind
                relevante_stuecklisten = [sl for sl in alle_stuecklisten if sl.projekt in projektnamen]
                
                if relevante_stuecklisten:
                    story.append(PageBreak())
                    for stueckliste in relevante_stuecklisten:
                        story.append(Spacer(1, 10*mm))
                        stueckliste_header = self._erstelle_stueckliste_kopfzeile(stueckliste, styles)
                        story.extend(stueckliste_header)
                        story.append(Spacer(1, 5*mm))
                        stueckliste_table = self._erstelle_stueckliste_tabelle(stueckliste, styles)
                        story.append(stueckliste_table)
                        story.append(Spacer(1, 5*mm))
                        stueckliste_footer = self._erstelle_stueckliste_fusszeile(stueckliste, styles)
                        story.extend(stueckliste_footer)
                        story.append(PageBreak())
        
        # PDF erstellen
        doc.build(story)
        
        return output_path
    
    def _erstelle_rechnung_kopfzeile(self, rechnung: Rechnung, styles) -> list:
        """Erstellt die Kopfzeile der Rechnung"""
        story = []
        
        config = self.manager.adapter.get_config()
        unternehmen = config.get("unternehmen", {})
        kunde = self.manager.get_kunde(rechnung.kunde_id)
        
        # Unternehmen-Info links
        unternehmen_text = f"<b>{unternehmen.get('name', '')}</b><br/>"
        if unternehmen.get('strasse'):
            unternehmen_text += f"{unternehmen['strasse']}<br/>"
        if unternehmen.get('plz') or unternehmen.get('ort'):
            unternehmen_text += f"{unternehmen.get('plz', '')} {unternehmen.get('ort', '')}<br/>"
        if unternehmen.get('telefon'):
            unternehmen_text += f"Tel: {unternehmen['telefon']}<br/>"
        if unternehmen.get('email'):
            unternehmen_text += f"E-Mail: {unternehmen['email']}"
        
        unternehmen_para = Paragraph(unternehmen_text, styles['Normal'])
        
        # Rechnungsinfo rechts
        rechnung_text = f"<b>RECHNUNG</b><br/><br/>"
        rechnung_text += f"<b>Rechnungsnummer:</b> {rechnung.rechnungsnummer}<br/>"
        rechnung_text += f"<b>Rechnungsdatum:</b> {rechnung.rechnungsdatum.strftime('%d.%m.%Y')}<br/>"
        rechnung_text += f"<b>Leistungsdatum:</b> {rechnung.leistungsdatum.strftime('%d.%m.%Y')}<br/>"
        rechnung_text += f"<b>Fälligkeitsdatum:</b> {rechnung.faelligkeitsdatum.strftime('%d.%m.%Y')}<br/>"
        rechnung_text += f"<b>Zahlungsart:</b> {rechnung.zahlungsart}"
        
        rechnung_para = Paragraph(rechnung_text, styles['Normal'])
        
        # Kunde
        kunde_text = ""
        if kunde:
            kunde_text = f"<b>Rechnungsempfänger:</b><br/>"
            kunde_text += f"{kunde.get_vollstaendiger_name()}<br/>"
            adresse = kunde.get_vollstaendige_adresse()
            if adresse:
                kunde_text += adresse.replace('\n', '<br/>')
        
        kunde_para = Paragraph(kunde_text, styles['Normal'])
        
        # Tabelle für Kopfzeile
        header_table = Table(
            [[unternehmen_para, rechnung_para]],
            colWidths=[100*mm, 70*mm],
            rowHeights=[60*mm]
        )
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 5*mm))
        story.append(kunde_para)
        
        return story
    
    def _erstelle_rechnung_positionen_tabelle(self, rechnung: Rechnung, styles) -> Table:
        """Erstellt die Tabelle mit Rechnungspositionen"""
        # Tabellenkopf
        data = [['Pos.', 'Bezeichnung', 'Menge', 'Einheit', 'Einzelpreis (€)', 'Gesamtpreis (€)']]
        
        # Positionen - Bezeichnung als Paragraph für Word-Wrap
        for index, position in enumerate(rechnung.positionen, start=1):
            # Bezeichnung als Paragraph für automatisches Word-Wrap
            bezeichnung_para = Paragraph(position.bezeichnung, styles['Normal'])
            
            data.append([
                str(index),
                bezeichnung_para,
                f"{position.menge:.2f}",
                position.einheit,
                f"{position.einzelpreis:.2f}",
                f"{position.gesamtpreis:.2f}"
            ])
        
        # Tabelle erstellen
        table = Table(
            data,
            colWidths=[15*mm, 70*mm, 25*mm, 25*mm, 30*mm, 30*mm],
            repeatRows=1
        )
        
        # Tabellenstil
        table_style = TableStyle([
            # Kopfzeile
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Datenzeilen
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Pos. zentriert
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Bezeichnung links
            ('ALIGN', (2, 1), (5, -1), 'RIGHT'),  # Zahlen rechts
            
            # Word-Wrap für Bezeichnung
            ('WORDWRAP', (1, 1), (1, -1), True),  # Word-Wrap für Bezeichnungsspalte
            ('VALIGN', (1, 1), (1, -1), 'TOP'),  # Bezeichnung oben ausrichten für mehrzeiligen Text
            
            # Rahmen
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ])
        
        table.setStyle(table_style)
        return table
    
    def _erstelle_rechnung_summen(self, rechnung: Rechnung, styles) -> list:
        """Erstellt die Summenzeile der Rechnung"""
        story = []
        
        # Summen rechtsbündig
        summen_text = f"Zwischensumme (netto): {rechnung.nettobetrag:.2f} €<br/>"
        summen_text += f"MwSt ({rechnung.mwst_satz:.1f}%): {rechnung.mwst_betrag:.2f} €<br/>"
        summen_text += f"<b>Gesamtbetrag (brutto): {rechnung.bruttobetrag:.2f} €</b>"
        
        summen_para = Paragraph(summen_text, styles['Normal'])
        
        # Tabelle für rechtsbündige Ausrichtung
        summen_table = Table(
            [[summen_para]],
            colWidths=[170*mm]
        )
        summen_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(summen_table)
        
        # Zahlungsziel und Bankverbindung
        story.append(Spacer(1, 10*mm))
        
        # Berechne Zahlungsziel in Tagen
        zahlungsziel_tage = (rechnung.faelligkeitsdatum - rechnung.rechnungsdatum).days
        
        # Lade Bankverbindung aus Config
        config = self.manager.adapter.get_config()
        unternehmen = config.get("unternehmen", {})
        
        zahlungsinfo_text = f"<b>Zahlungsziel:</b> {zahlungsziel_tage} Tage<br/>"
        zahlungsinfo_text += f"<b>Fälligkeitsdatum:</b> {rechnung.faelligkeitsdatum.strftime('%d.%m.%Y')}<br/><br/>"
        
        # Bankverbindung
        if unternehmen.get('iban') or unternehmen.get('bic') or unternehmen.get('bank'):
            zahlungsinfo_text += f"<b>Bankverbindung:</b><br/>"
            if unternehmen.get('bank'):
                zahlungsinfo_text += f"{unternehmen['bank']}<br/>"
            if unternehmen.get('iban'):
                zahlungsinfo_text += f"IBAN: {unternehmen['iban']}<br/>"
            if unternehmen.get('bic'):
                zahlungsinfo_text += f"BIC: {unternehmen['bic']}<br/>"
        
        zahlungsinfo_para = Paragraph(zahlungsinfo_text, styles['Normal'])
        story.append(zahlungsinfo_para)
        
        # Notizen
        if rechnung.notizen:
            story.append(Spacer(1, 10*mm))
            notizen_text = f"<b>Hinweise:</b><br/>{rechnung.notizen}"
            notizen_para = Paragraph(notizen_text, styles['Normal'])
            story.append(notizen_para)
        
        return story

