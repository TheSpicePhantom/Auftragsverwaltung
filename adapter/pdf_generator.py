"""
PDF-Generator für Rechnungen, Angebote und Lieferscheine
GoBD-konform, §14 UStG-konform und DIN 5008 Layout
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Frame, PageTemplate
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Dict, Any, Optional
import os


class PDFGenerator:
    """Generiert professionelle PDFs für Rechnungen, Angebote etc."""
    
    # DIN 5008 Konstanten für Briefkopf
    ADRESSFELD_VON_OBEN = 45*mm  # Standard: 45mm von oben
    ADRESSFELD_VON_LINKS = 20*mm  # Standard: 20mm von links
    ADRESSFELD_BREITE = 85*mm
    ADRESSFELD_HOEHE = 40*mm
    
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: Konfigurationsdictionary mit Unternehmensdaten
        """
        self.config = config
        self.unternehmen = config.get('unternehmen', {})
        self.rechnung_config = config.get('rechnung', {})
        
    def rechnung_erstellen(self, 
                           rechnung: Dict[str, Any], 
                           kunde: Dict[str, Any],
                           ausgabepfad: str,
                           logo_pfad: Optional[str] = None) -> str:
        """
        Erstellt eine Rechnung als PDF (DIN 5008 konform)
        
        Args:
            rechnung: Rechnungsdaten (Dict aus Rechnung.to_dict())
            kunde: Kundendaten (Dict aus Kunde.to_dict())
            ausgabepfad: Pfad für die PDF-Datei
            logo_pfad: Optionaler Pfad zum Firmenlogo
            
        Returns:
            Pfad zur erstellten PDF-Datei
        """
        # PDF erstellen mit custom Canvas für Header/Footer
        doc = SimpleDocTemplate(
            ausgabepfad,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=105*mm,  # Platz für Briefkopf + Adressfeld
            bottomMargin=20*mm
        )
        
        # Story (Inhalt) aufbauen
        story = []
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=15,
            spaceBefore=10
        )
        
        # Rechnungskopf
        story.append(Paragraph("RECHNUNG", title_style))
        
        # Rechnungsdetails (rechts neben dem Titel)
        rechnungsdatum = datetime.fromisoformat(rechnung['rechnungsdatum'])
        leistungsdatum = datetime.fromisoformat(rechnung['leistungsdatum'])
        faelligkeitsdatum = datetime.fromisoformat(rechnung['faelligkeitsdatum'])
        
        details_data = [
            ['Rechnungsnummer:', rechnung['rechnungsnummer']],
            ['Rechnungsdatum:', rechnungsdatum.strftime('%d.%m.%Y')],
            ['Leistungsdatum:', leistungsdatum.strftime('%d.%m.%Y')],
            ['Fälligkeitsdatum:', faelligkeitsdatum.strftime('%d.%m.%Y')],
            ['Kundennummer:', kunde.get('id', 'N/A')],
        ]
        
        details_table = Table(details_data, colWidths=[50*mm, 60*mm])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 10*mm))
        
        # Anrede
        # Verbesserte Anrede: Firma hat Vorrang, sonst Name
        if kunde.get('firma'):
            anrede = f"Sehr geehrte Damen und Herren,"
        elif kunde.get('name'):
            # Wenn Vorname vorhanden, verwende "Herr/Frau Vorname Name", sonst nur Name
            if kunde.get('vorname'):
                anrede = f"Sehr geehrte/r {kunde.get('vorname', '')} {kunde.get('name', '')},"
            else:
                anrede = f"Sehr geehrte/r {kunde.get('name', '')},"
        else:
            anrede = "Sehr geehrte Damen und Herren,"
        story.append(Paragraph(anrede, styles['Normal']))
        story.append(Spacer(1, 5*mm))
        
        # Einleitung mit Auftragsnummer
        auftragsnummer = rechnung.get('auftragsnummer', '')
        if auftragsnummer:
            intro_text = f"hiermit erlauben wir uns, Ihnen die Leistungen zu Auftrag {auftragsnummer} in Rechnung zu stellen:"
        else:
            intro_text = "hiermit erlauben wir uns, Ihnen folgende Leistungen in Rechnung zu stellen:"
        story.append(Paragraph(intro_text, styles['Normal']))
        story.append(Spacer(1, 8*mm))
        
        # Positionstabelle
        # Paragraph-Style für Beschreibung mit Word-Wrap
        beschreibung_style = ParagraphStyle(
            'BeschreibungStyle',
            parent=styles['Normal'],
            fontSize=9,
            wordWrap='CJK',  # Ermöglicht Word-Wrap
            leading=10.8  # Zeilenhöhe
        )
        
        pos_data = [['Pos.', 'Beschreibung', 'Menge', 'Einheit', 'Einzelpreis', 'Gesamt']]
        
        for idx, pos in enumerate(rechnung['positionen'], 1):
            beschreibung_text = pos.get('beschreibung', pos.get('bezeichnung', ''))
            pos_data.append([
                str(idx),
                Paragraph(beschreibung_text, beschreibung_style),
                f"{pos.get('menge', 0):.2f}",
                pos.get('einheit', 'Stk'),
                f"{pos.get('einzelpreis', 0):.2f} €",
                f"{pos.get('gesamtpreis', 0):.2f} €"
            ])
        
        pos_table = Table(pos_data, colWidths=[10*mm, 70*mm, 20*mm, 20*mm, 25*mm, 25*mm])
        pos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # TOP statt MIDDLE für mehrzeilige Beschreibungen
        ]))
        story.append(pos_table)
        story.append(Spacer(1, 5*mm))
        
        # Summen
        summen_data = [
            ['', '', '', '', 'Nettobetrag:', f"{rechnung['nettobetrag']:.2f} €"],
            ['', '', '', '', f"zzgl. {rechnung['mwst_satz']:.0f}% MwSt:", f"{rechnung['mwst_betrag']:.2f} €"],
            ['', '', '', '', 'Rechnungsbetrag:', f"{rechnung['bruttobetrag']:.2f} €"],
        ]
        
        summen_table = Table(summen_data, colWidths=[10*mm, 70*mm, 20*mm, 20*mm, 25*mm, 25*mm])
        summen_table.setStyle(TableStyle([
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
            ('ALIGN', (5, 0), (5, -1), 'RIGHT'),
            ('FONTNAME', (4, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (4, 0), (-1, -1), 10),
            ('LINEABOVE', (4, 0), (5, 0), 0.5, colors.grey),
            ('LINEABOVE', (4, -1), (5, -1), 2, colors.black),
            ('FONTSIZE', (4, -1), (5, -1), 12),
        ]))
        story.append(summen_table)
        story.append(Spacer(1, 10*mm))
        
        # Zahlungshinweis
        zahlungstext = f"""Wir bitten Sie, den <b>Rechnungsbetrag von {rechnung['bruttobetrag']:.2f} €</b> 
        bis zum <b>{faelligkeitsdatum.strftime('%d.%m.%Y')}</b> unter Angabe der Rechnungsnummer 
        <b>{rechnung['rechnungsnummer']}</b> auf unser Konto zu überweisen:"""
        
        story.append(Paragraph(zahlungstext, styles['Normal']))
        story.append(Spacer(1, 5*mm))
        
        # Bankverbindung
        bank_data = [
            ['Kontoinhaber:', self.unternehmen.get('name', '')],
            ['Bank:', self.unternehmen.get('bank', '')],
            ['IBAN:', self.unternehmen.get('iban', '')],
            ['BIC:', self.unternehmen.get('bic', '')],
        ]
        
        bank_table = Table(bank_data, colWidths=[35*mm, 95*mm])
        bank_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
            ('LEFTPADDING', (0, 0), (-1, -1), 3*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3*mm),
            ('TOPPADDING', (0, 0), (-1, -1), 2*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2*mm),
        ]))
        story.append(bank_table)
        story.append(Spacer(1, 10*mm))
        
        # Hinweise
        if rechnung.get('notizen'):
            story.append(Paragraph(f"<b>Hinweise:</b> {rechnung['notizen']}", styles['Normal']))
            story.append(Spacer(1, 5*mm))
        
        story.append(Paragraph("Vielen Dank für Ihren Auftrag und Ihr Vertrauen!", styles['Normal']))
        story.append(Spacer(1, 8*mm))
        story.append(Paragraph("Mit freundlichen Grüßen", styles['Normal']))
        story.append(Spacer(1, 15*mm))
        story.append(Paragraph(self.unternehmen.get('name', ''), styles['Normal']))
        
        # PDF erstellen mit custom Header/Footer
        doc.build(
            story, 
            onFirstPage=lambda c, d: self._add_header_footer(c, d, kunde, logo_pfad, True),
            onLaterPages=lambda c, d: self._add_header_footer(c, d, kunde, logo_pfad, False)
        )
        
        return ausgabepfad
    
    def _add_header_footer(self, canvas_obj, doc, kunde: Dict[str, Any], logo_pfad: Optional[str], is_first_page: bool):
        """Fügt Header und Footer hinzu (DIN 5008 konform)"""
        canvas_obj.saveState()
        
        if is_first_page:
            # Logo (rechts oben)
            if logo_pfad and os.path.exists(logo_pfad):
                canvas_obj.drawImage(
                    logo_pfad,
                    A4[0] - 70*mm,  # Rechts
                    A4[1] - 35*mm,  # Oben
                    width=50*mm,
                    height=25*mm,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            
            # Firmenadresse (links oben, klein)
            canvas_obj.setFont('Helvetica', 7)
            y_pos = A4[1] - 15*mm
            canvas_obj.drawString(20*mm, y_pos, self.unternehmen.get('name', ''))
            y_pos -= 3.5*mm
            canvas_obj.drawString(20*mm, y_pos, f"{self.unternehmen.get('strasse', '')}")
            y_pos -= 3.5*mm
            canvas_obj.drawString(20*mm, y_pos, f"{self.unternehmen.get('plz', '')} {self.unternehmen.get('ort', '')}")
            
            # Absenderzeile (DIN 5008 Rücksendeangabe)
            canvas_obj.setFont('Helvetica', 6)
            absender_zeile = f"{self.unternehmen.get('name', '')} • {self.unternehmen.get('strasse', '')} • {self.unternehmen.get('plz', '')} {self.unternehmen.get('ort', '')}"
            
            # Linie unter Absenderzeile
            canvas_obj.line(
                self.ADRESSFELD_VON_LINKS,
                A4[1] - (self.ADRESSFELD_VON_OBEN - 5*mm),
                self.ADRESSFELD_VON_LINKS + self.ADRESSFELD_BREITE,
                A4[1] - (self.ADRESSFELD_VON_OBEN - 5*mm)
            )
            
            canvas_obj.drawString(
                self.ADRESSFELD_VON_LINKS,
                A4[1] - (self.ADRESSFELD_VON_OBEN - 3*mm),
                absender_zeile
            )
            
            # Empfängeradresse (im Sichtfenster)
            canvas_obj.setFont('Helvetica', 11)
            y_pos = A4[1] - self.ADRESSFELD_VON_OBEN - 3*mm
            
            # Firma oder Name
            if kunde.get('firma'):
                canvas_obj.drawString(self.ADRESSFELD_VON_LINKS, y_pos, kunde.get('firma', ''))
                y_pos -= 5*mm
                if kunde.get('name'):
                    canvas_obj.setFont('Helvetica', 10)
                    canvas_obj.drawString(self.ADRESSFELD_VON_LINKS, y_pos, f"z.H. {kunde.get('name', '')}")
                    y_pos -= 5*mm
                    canvas_obj.setFont('Helvetica', 11)
            else:
                canvas_obj.drawString(self.ADRESSFELD_VON_LINKS, y_pos, kunde.get('name', ''))
                y_pos -= 5*mm
            
            # Straße
            canvas_obj.drawString(self.ADRESSFELD_VON_LINKS, y_pos, kunde.get('strasse', ''))
            y_pos -= 5*mm
            
            # PLZ und Ort
            canvas_obj.drawString(self.ADRESSFELD_VON_LINKS, y_pos, f"{kunde.get('plz', '')} {kunde.get('ort', '')}")
        
        # Fußzeile (§14 UStG Pflichtangaben) - auf jeder Seite
        canvas_obj.setFont('Helvetica', 7)
        canvas_obj.setFillColor(colors.grey)
        
        # Trennlinie
        canvas_obj.line(20*mm, 25*mm, A4[0] - 20*mm, 25*mm)
        
        # Fußzeile Text
        footer_lines = [
            f"{self.unternehmen.get('name', '')} • {self.unternehmen.get('strasse', '')} • {self.unternehmen.get('plz', '')} {self.unternehmen.get('ort', '')}",
            f"Tel: {self.unternehmen.get('telefon', '')} • E-Mail: {self.unternehmen.get('email', '')}",
            f"USt-IdNr: {self.unternehmen.get('ust_id', '')} • Bank: {self.unternehmen.get('bank', '')} • IBAN: {self.unternehmen.get('iban', '')}"
        ]
        
        y_pos = 22*mm
        for line in footer_lines:
            canvas_obj.drawCentredString(A4[0] / 2, y_pos, line)
            y_pos -= 3*mm
        
        # Seitenzahl
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.drawRightString(
            A4[0] - 20*mm,
            10*mm,
            f"Seite {doc.page}"
        )
        
        canvas_obj.restoreState()
