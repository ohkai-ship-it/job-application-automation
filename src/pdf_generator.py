"""
Enhanced PDF Generator for Cover Letters
Creates professional cover letter PDFs matching your style guide
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, PageTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import HRFlowable

from datetime import datetime
import os
from typing import Dict, Any

# Logging and error types
try:
    from .utils.log_config import get_logger
    from .utils.errors import DocumentError
except Exception:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.log_config import get_logger
    from utils.errors import DocumentError


class CoverLetterPDF:
    """
    Generates formatted cover letter PDFs matching your personal style
    """
    
    def __init__(self) -> None:
        self.page_width, self.page_height = A4
        self.margin_left = 2.5 * cm
        self.margin_right = 2.5 * cm
        self.margin_top = 2.5 * cm
        self.margin_bottom = 2 * cm
        
        # Your personal details
        self.sender = {
            'name': 'Dr. Kai Voges',
            'phone': '+49 1622146092',
            'email': 'kai.voges@gmx.net',
            'address_line1': 'Cranachstraße 4',
            'address_line2': '40235 Düsseldorf',
            'linkedin': 'www.linkedin.com/in/worldapprentice'
        }
        
        # Color scheme (professional blue-gray palette)
        self.colors = {
            'primary': colors.HexColor('#2C3E50'),      # Dark blue-gray for headers
            'secondary': colors.HexColor('#34495E'),    # Medium gray for text
            'accent': colors.HexColor('#3498DB'),       # Blue accent
            'text': colors.HexColor('#2C3E50'),         # Body text
            'light_gray': colors.HexColor('#95A5A6')   # Light gray for lines
        }
        # logger and error types are imported at module level
    
    def generate_pdf(
        self,
        cover_letter_text: str,
        job_data: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Generate a formatted PDF cover letter
        
        Args:
            cover_letter_text (str): The cover letter content
            job_data (dict): Job information (company, title, etc.)
            output_path (str): Where to save the PDF
            
        Returns:
            str: Path to generated PDF
        """
        logger = get_logger(__name__)
        logger.info("Generating PDF | out=%s", output_path)

        # Ensure directory exists
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        except Exception as e:
            logger.error("Failed to prepare output directory for PDF %s: %s", output_path, e)
            raise DocumentError(f"Failed to prepare output directory: {output_path}") from e

        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=self.margin_right,
            leftMargin=self.margin_left,
            topMargin=self.margin_top,
            bottomMargin=self.margin_bottom
        )

        # Container for PDF content
        story = []

        # Define styles
        styles = self._create_styles()

        # Detect language for proper greetings
        language = self._detect_language(cover_letter_text)

        # Get job details
        company_name = job_data.get('company_name', 'Company')
        job_title = job_data.get('job_title', 'Position')
        company_address = job_data.get('company_address', '')
        
        # Build the document
        # Company address - no left padding, will align naturally with body text
        company_lines = [f"<b>{company_name}</b>"]
        if company_address:
            address_clean = company_address.replace(company_name, '').strip()
            if address_clean:
                # Split address into lines if it's long
                address_parts = address_clean.split(',')
                for part in address_parts[:3]:  # Max 3 lines
                    if part.strip():
                        company_lines.append(part.strip())

        # Build company address paragraphs
        company_paragraphs = []
        for line in company_lines:
            company_paragraphs.append(Paragraph(line, styles['recipient']))

        # Sender info (right-aligned)
        sender_lines = [
            f"<b>{self.sender['name']}</b>",
            self.sender['phone'],
            self.sender['email'],
            self.sender['address_line1'],
            self.sender['address_line2']
        ]

        # Create sender as a mini-table (right-aligned text)
        sender_cell = []
        for i, line in enumerate(sender_lines):
            if i == 0:
                sender_cell.append([Paragraph(line, styles['sender_name'])])
            else:
                sender_cell.append([Paragraph(line, styles['sender_info'])])

        sender_mini_table = Table(sender_cell, colWidths=[6*cm])
        sender_mini_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))

        # Place sender info at top right
        sender_wrapper = Table(
            [[Paragraph('', styles['normal']), sender_mini_table]],
            colWidths=[10*cm, 6*cm]
        )
        sender_wrapper.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        story.append(sender_wrapper)
        story.append(Spacer(1, 0.5*cm))

        # Company address - left-aligned, same as body text
        for para in company_paragraphs:
            story.append(para)

        story.append(Spacer(1, 1*cm))

        # Date (right-aligned, close to right border)
        today = datetime.now().strftime('%d.%m.%Y')
        date_table = Table(
            [[Paragraph('', styles['normal']), Paragraph(today, styles['date'])]],
            colWidths=[13.5*cm, 2.5*cm]
        )
        date_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(date_table)
        story.append(Spacer(1, 1.5*cm))

        # Subject line (bold, left-aligned)
        subject = f"Bewerbung als {job_title}" if language == 'german' else f"Application for {job_title}"
        story.append(Paragraph(f"<b>{subject}</b>", styles['subject']))
        story.append(Spacer(1, 0.8*cm))

        # Greeting
        greeting = f"Hallo liebes {company_name}-Team," if language == 'german' else "Dear Hiring Team,"
        story.append(Paragraph(greeting, styles['greeting']))
        story.append(Spacer(1, 0.5*cm))

        # Cover letter body (justified text, proper spacing)
        paragraphs = cover_letter_text.split('\n\n')
        for i, para in enumerate(paragraphs):
            if para.strip():
                story.append(Paragraph(para.strip(), styles['body']))
                # Add spacing between paragraphs
                if i < len(paragraphs) - 1:
                    story.append(Spacer(1, 0.4*cm))

        story.append(Spacer(1, 0.8*cm))

        # Closing
        closing = "Mit freundlichen Grüßen," if language == 'german' else "Best regards,"
        story.append(Paragraph(closing, styles['closing']))
        story.append(Spacer(1, 1.5*cm))

        # Signature
        story.append(Paragraph(f"<b>{self.sender['name']}</b>", styles['signature']))

        # Attachments
        story.append(Spacer(1, 1.5*cm))
        attachments = "<i>Anlagen: Deckblatt · Lebenslauf · Zeugnisse</i>" if language == 'german' else "<i>Attachments: Cover Page · Resume · References</i>"
        story.append(Paragraph(attachments, styles['attachments']))

        # LinkedIn at bottom
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(f"<i>{self.sender['linkedin']}</i>", styles['attachments']))

        # Build PDF
        try:
            doc.build(story)
            logger.info("PDF generated: %s", output_path)
            return output_path
        except Exception as e:
            logger.error("Failed to generate PDF %s: %s", output_path, e)
            raise DocumentError(f"Failed to generate PDF: {output_path}") from e
    
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles"""
        
        styles = {}
        
        # Sender name (bold, slightly larger)
        styles['sender_name'] = ParagraphStyle(
            'SenderName',
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            textColor=self.colors['primary'],
            alignment=TA_LEFT
        )
        styles['sender_info'] = ParagraphStyle(
            'SenderInfo',
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=self.colors['secondary'],
            alignment=TA_LEFT
        )
        
        # Recipient address
        styles['recipient'] = ParagraphStyle(
            'Recipient',
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=self.colors['text'],
            spaceAfter=2
        )
        
        # Date
        styles['date'] = ParagraphStyle(
            'Date',
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=self.colors['text']
        )
        
        # Subject line
        styles['subject'] = ParagraphStyle(
            'Subject',
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=15,
            textColor=self.colors['primary']
        )
        
        # Greeting
        styles['greeting'] = ParagraphStyle(
            'Greeting',
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=self.colors['text']
        )
        
        # Body text (justified, professional spacing)
        styles['body'] = ParagraphStyle(
            'Body',
            fontName='Helvetica',
            fontSize=11,
            leading=17,  # 1.5 line spacing
            textColor=self.colors['text'],
            alignment=TA_JUSTIFY,
            firstLineIndent=0
        )
        
        # Closing
        styles['closing'] = ParagraphStyle(
            'Closing',
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=self.colors['text']
        )
        
        # Signature
        styles['signature'] = ParagraphStyle(
            'Signature',
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=self.colors['primary']
        )
        
        # Attachments note
        styles['attachments'] = ParagraphStyle(
            'Attachments',
            fontName='Helvetica',
            fontSize=9,
            leading=11,
            textColor=self.colors['light_gray']
        )
        
        # Normal (for spacing hacks)
        styles['normal'] = ParagraphStyle(
            'Normal',
            fontName='Helvetica',
            fontSize=11,
            leading=14
        )
        
        return styles
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        german_words = ['und', 'der', 'die', 'das', 'ich', 'bei', 'mit', 'für']
        count = sum(1 for word in german_words if word in text.lower())
        return 'german' if count >= 3 else 'english'


# Test function
if __name__ == "__main__":
    # Test with sample data
    test_cover_letter = """Die STRABAG AG beeindruckt mich durch ihren innovativen Ansatz und das Engagement für nachhaltiges Bauen. Als erfahrener Produktmanager mit umfangreicher Expertise in der digitalen Transformation sehe ich großes Potenzial, zur strategischen Weiterentwicklung Ihrer Digital Workplace Lösungen beizutragen.

In meiner letzten Position bei von Rundstedt habe ich eine umfassende strategische Vision für ein digitales B2B-Portfolio entwickelt, das Marktchancen von über 20 Millionen Euro umfasst. Ich leitete ein cross-funktionales Team von zehn Mitgliedern und verantwortete die Finanzierung von über 200.000 Euro. Dabei konnte ich die Kommerzialisierung von vier Produkten erfolgreich steuern und dabei mehr als 30 Consultants in die Prozesse integrieren.

Zusätzlich habe ich als Co-Founder und CEO eines Start-ups in der KI- und Drohnentechnologie ein Team von 15 Personen aufgebaut und alle technischen Aspekte geleitet. Mein Fokus auf Nutzererfahrung und Wettbewerbsfähigkeit führte zu signifikanten Verbesserungen und Auszeichnungen.

Meine analytischen Fähigkeiten sowie meine Erfahrung in der Roadmap-Planung und Priorisierung von Features machen mich zu einem geeigneten Kandidaten für die Position des Product Managers. Ich bin hochmotiviert, mein Know-how bei STRABAG einzubringen und gemeinsam an der Zukunft des Bauens zu arbeiten."""
    
    test_job_data = {
        'company_name': 'STRABAG AG',
        'company_address': 'Albstadtweg 10, 70567 Stuttgart',
        'job_title': 'Product Manager Digital Workplace (m/w/d)',
        'location': 'Stuttgart'
    }
    
    print("=" * 80)
    print("ENHANCED PDF GENERATOR TEST")
    print("=" * 80)
    
    generator = CoverLetterPDF()
    output_file = "output/cover_letters/test_cover_letter_styled.pdf"
    
    pdf_path = generator.generate_pdf(test_cover_letter, test_job_data, output_file)
    
    print(f"\n✓ Test complete!")
    print(f"✓ PDF saved to: {pdf_path}")
    print(f"\nOpen the PDF to see the enhanced formatting:")
    print(f"  - Professional color scheme")
    print(f"  - Proper spacing and alignment")
    print(f"  - Right-aligned sender info")
    print(f"  - Justified body text")
    print(f"  - Bold subject line")