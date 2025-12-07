"""
PDF-Generator für Rechnungen, Angebote und Lieferscheine
GoBD-konform und §14 UStG-konform
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Dict, Any, Optional
import os


class PDFGenerator:
    """Generiert professionelle PDFs für Rechnungen, Angebote etc."""
    
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
        Erstellt eine Rechnung als PDF
        
        Args:
            rechnung: Rechnungsdaten (Dict aus Rechnung.to_dict())
            kunde: Kundendaten (Dict aus Kunde.to_dict())
            ausgabepfad: Pfad für die PDF-Datei
            logo_pfad: Optionaler Pfad zum Firmenlogo
            
        Returns:
            Pfad zur erstellten PDF-Datei
        """
        # PDF erstellen
        doc = SimpleDocTemplate(
            ausgabepfad,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Story (Inhalt) aufbauen
        story = []
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30
        )
        
        # Logo und Firmendaten (Kopfzeile)
        header_data = []
        if logo_pfad and os.path.exists(logo_pfad):
            logo = Image(logo_pfad, width=50*mm, height=25*mm)
            header_data.append([logo, self._get_firmen_adresse()])
        else:
            header_data.append([self._get_firmen_adresse(), ''])
        
        header_table = Table(header_data, colWidths=[90*mm, 80*mm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10*mm))
        
        # Kundenadresse
        story.append(self._get_kunden_adresse(kunde))
        story.append(Spacer(1, 10*mm))
        
        # Rechnungskopf
        story.append(Paragraph("RECHNUNG", title_style))
        
        # Rechnungsdetails
        rechnungsdatum = datetime.fromisoformat(rechnung['rechnungsdatum'])
        leistungsdatum = datetime.fromisoformat(rechnung['leistungsdatum'])
        faelligkeitsdatum = datetime.fromisoformat(rechnung['faelligkeitsdatum'])
        
        details_data = [
            ['Rechnungsnummer:', rechnung['rechnungsnummer']],
            ['Rechnungsdatum:', rechnungsdatum.strftime('%d.%m.%Y')],
            ['Leistungsdatum:', leistungsdatum.strftime('%d.%m.%Y')],
            ['Fälligkeitsdatum:', faelligkeitsdatum.strftime('%d.%m.%Y')],
            ['Kundennummer:', kunde.get('kundennummer', 'N/A')],
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
        
        # Positionen
        story.append(Paragraph("Leistungen", styles['Heading2']))
        story.append(Spacer(1, 5*mm))
        
        # Positionstabelle
        pos_data = [['Pos.', 'Beschreibung', 'Menge', 'Einheit', 'Einzelpreis', 'Gesamt']]
        
        for idx, pos in enumerate(rechnung['positionen'], 1):
            pos_data.append([
                str(idx),
                pos['beschreibung'],
                f"{pos['menge']:.2f}",
                pos['einheit'],
                f"{pos['einzelpreis']:.2f} €",
                f"{pos['gesamtpreis']:.2f} €"
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
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(pos_table)
        story.append(Spacer(1, 5*mm))
        
        # Summen
        summen_data = [
            ['', '', '', '', 'Nettobetrag:', f"{rechnung['nettobetrag']:.2f} €"],
            ['', '', '', '', f"zzgl. {rechnung['mwst_satz']:.0f}% MwSt:", f"{rechnung['mwst_betrag']:.2f} €"],
            ['', '', '', '', 'Bruttobetrag:', f"{rechnung['bruttobetrag']:.2f} €"],
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
        zahlungstext = f"""Bitte überweisen Sie den Betrag von <b>{rechnung['bruttobetrag']:.2f} €</b> 
        bis zum <b>{faelligkeitsdatum.strftime('%d.%m.%Y')}</b> unter Angabe der Rechnungsnummer 
        <b>{rechnung['rechnungsnummer']}</b> auf folgendes Konto:"""
        
        story.append(Paragraph(zahlungstext, styles['Normal']))
        story.append(Spacer(1, 5*mm))
        
        # Bankverbindung
        bank_data = [
            ['Bank:', self.unternehmen.get('bank', '')],
            ['IBAN:', self.unternehmen.get('iban', '')],
            ['BIC:', self.unternehmen.get('bic', '')],
        ]
        
        bank_table = Table(bank_data, colWidths=[30*mm, 80*mm])
        bank_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(bank_table)
        story.append(Spacer(1, 10*mm))
        
        # Fußnote (§14 UStG Pflichtangaben)
        if rechnung.get('notizen'):
            story.append(Paragraph(f"<b>Hinweise:</b> {rechnung['notizen']}", styles['Normal']))
            story.append(Spacer(1, 5*mm))
        
        story.append(Paragraph("Vielen Dank für Ihren Auftrag!", styles['Normal']))
        
        # Fußzeile
        story.append(Spacer(1, 15*mm))
        story.append(self._get_footer())
        
        # PDF erstellen
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
        return ausgabepfad
    
    def _get_firmen_adresse(self) -> Paragraph:
        """Erstellt Firmenadresse als Paragraph"""
        styles = getSampleStyleSheet()
        firma_text = f"""<b>{self.unternehmen.get('name', '')}</b><br/>
        {self.unternehmen.get('strasse', '')}<br/>
        {self.unternehmen.get('plz', '')} {self.unternehmen.get('ort', '')}<br/>
        Tel: {self.unternehmen.get('telefon', '')}<br/>
        {self.unternehmen.get('email', '')}"""
        return Paragraph(firma_text, styles['Normal'])
    
    def _get_kunden_adresse(self, kunde: Dict[str, Any]) -> Table:
        """Erstellt Kundenadresse"""
        kunde_text = f"""{kunde.get('firma', kunde.get('name', ''))}<br/>
        {kunde.get('strasse', '')}<br/>
        {kunde.get('plz', '')} {kunde.get('ort', '')}"""
        
        styles = getSampleStyleSheet()
        data = [[Paragraph(kunde_text, styles['Normal'])]]
        table = Table(data, colWidths=[90*mm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 5*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5*mm),
            ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
        ]))
        return table
    
    def _get_footer(self) -> Table:
        """Erstellt Fußzeile mit Pflichtangaben §14 UStG"""
        styles = getSampleStyleSheet()
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.grey
        )
        
        footer_text = f"""{self.unternehmen.get('name', '')} | 
        {self.unternehmen.get('strasse', '')} | 
        {self.unternehmen.get('plz', '')} {self.unternehmen.get('ort', '')}<br/>
        Telefon: {self.unternehmen.get('telefon', '')} | 
        E-Mail: {self.unternehmen.get('email', '')}<br/>
        USt-IdNr.: {self.unternehmen.get('ust_id', '')} | 
        Bankverbindung: {self.unternehmen.get('bank', '')} | 
        IBAN: {self.unternehmen.get('iban', '')}"""
        
        data = [[Paragraph(footer_text, footer_style)]]
        table = Table(data, colWidths=[170*mm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
        ]))
        return table
    
    def _add_page_number(self, canvas_obj, doc):
        """Fügt Seitenzahl hinzu"""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.drawRightString(
            200*mm, 
            10*mm, 
            f"Seite {doc.page}"
        )
        canvas_obj.restoreState()
