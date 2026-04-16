from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BASE_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = BASE_DIR / "docs"
ASSETS_DIR = DOCS_DIR / "assets"
OUTPUT_PDF = DOCS_DIR / "Project-Documentation.pdf"


def register_fonts():
    fonts_dir = Path("C:/Windows/Fonts")
    pdfmetrics.registerFont(TTFont("Arial", str(fonts_dir / "arial.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Bold", str(fonts_dir / "arialbd.ttf")))


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BodyArial",
            fontName="Arial",
            fontSize=12,
            leading=16,
            alignment=4,
            textColor=colors.HexColor("#1f2937"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="HeadingArial",
            fontName="Arial-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#0a4f94"),
            spaceBefore=0,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubHeadingArial",
            fontName="Arial-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1f2937"),
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CaptionArial",
            fontName="Arial",
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#4b5563"),
            spaceAfter=6,
        )
    )
    return styles


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 10)
    canvas.setFillColor(colors.HexColor("#4b5563"))
    canvas.drawRightString(A4[0] - 16 * mm, 10 * mm, str(doc.page))
    canvas.restoreState()


def paragraph(text, style):
    return Paragraph(text, style)


def bullet_paragraph(text, style):
    return Paragraph(f"&bull; {text}", style)


def fit_image(path, max_width, max_height):
    image = ImageReader(str(path))
    width, height = image.getSize()
    scale = min(max_width / width, max_height / height)
    return Image(str(path), width=width * scale, height=height * scale)


def build_document():
    register_fonts()
    styles = build_styles()

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="P2P Process Implementation in SAP MM for BuildRight Construction",
        author="OpenAI Codex",
    )

    story = []

    story.append(paragraph("P2P Process Implementation in SAP MM for BuildRight Construction Pvt. Ltd.", styles["HeadingArial"]))
    story.append(
        paragraph(
            "This project presents an industry-grade Procure-to-Pay solution modeled on SAP MM business processes for BuildRight Construction Pvt. Ltd. The application covers the full purchasing cycle from internal material requirement to vendor settlement, supported by a Python backend, SQLite persistence, SAP-style user interface, and business control logic.",
            styles["BodyArial"],
        )
    )
    story.append(paragraph("Problem Statement", styles["SubHeadingArial"]))
    story.append(
        paragraph(
            "Manual procurement in a construction materials business creates operational and financial risk. Demand requests may be duplicated, supplier quotations may not be compared systematically, stock receipts can be delayed in recording, and finance teams may process invoices before confirming actual goods receipt. These conditions lead to over-ordering, invoice mismatch, duplicate payment risk, and weak audit traceability. A controlled P2P process resolves these issues through structured documents, posting discipline, and integrated accounting impact.",
            styles["BodyArial"],
        )
    )
    story.append(paragraph("Solution and Features", styles["SubHeadingArial"]))
    for item in [
        "Purchase Requisition creation for internal demand capture.",
        "RFQ and quotation recording for supplier enquiry and price comparison.",
        "Purchase Order creation with vendor, quantity, and negotiated price.",
        "Goods Receipt posting with inventory recognition and GR/IR accounting.",
        "Invoice Verification with quantity and value validation against PO and GR.",
        "Vendor Payment processing with liability clearance and bank posting.",
    ]:
        story.append(bullet_paragraph(item, styles["BodyArial"]))

    meta_data = [
        ["Company Code", "BR01", "Plant", "BR01 (Delhi)"],
        ["Purchasing Organization", "BR10", "Purchasing Group", "BR1"],
        ["Vendor", "SteelCo Supplies Ltd.", "Material", "STL001 - Structural Steel Rods"],
    ]
    meta_table = Table(meta_data, colWidths=[42 * mm, 48 * mm, 48 * mm, 42 * mm])
    meta_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Arial"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef4fa")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(Spacer(1, 4))
    story.append(meta_table)
    story.append(PageBreak())

    story.append(paragraph("Tech Stack", styles["SubHeadingArial"]))
    for item in [
        "Frontend: HTML5, CSS3, JavaScript",
        "Backend: Python 3.11 web server with REST-style endpoints",
        "Database: SQLite for persistent transaction and posting storage",
        "Business Domain: SAP MM Procure-to-Pay with MM-FI style integration",
        "Deployment: Localhost application packaged for ZIP and GitHub publishing",
    ]:
        story.append(bullet_paragraph(item, styles["BodyArial"]))

    story.append(paragraph("Unique Points", styles["SubHeadingArial"]))
    for item in [
        "Implements the complete P2P lifecycle in a working full-stack application rather than static mock screens only.",
        "Uses realistic document sequencing for PR, RFQ, quotation, PO, goods receipt, invoice, payment, and FI documents.",
        "Enforces 3-way match visibility between Purchase Order, Goods Receipt, and Invoice quantity or value.",
        "Blocks payment when invoice variance exceeds PO or GR values, demonstrating compliance control.",
        "Provides SAP-style transaction workspace, document history, and accounting ledger for evaluator demonstration.",
    ]:
        story.append(bullet_paragraph(item, styles["BodyArial"]))

    story.append(paragraph("Business Value", styles["SubHeadingArial"]))
    story.append(
        paragraph(
            "The project improves procurement visibility, supports auditability, reduces duplicate payment risk, and demonstrates how purchasing and finance activities remain connected through accounting entries. It also creates a stronger academic submission because it combines functional software, business logic, screenshots, and documentation in one deliverable.",
            styles["BodyArial"],
        )
    )
    story.append(PageBreak())

    story.append(paragraph("Application Screenshots", styles["SubHeadingArial"]))
    for filename, caption in [
        ("overview.png", "Figure 1. SAP-style overview cockpit showing process metrics and lifecycle monitor."),
        ("transactions.png", "Figure 2. Transaction processing workspace used to create and post MM documents."),
        ("documents.png", "Figure 3. Generated document register with business status and reference values."),
    ]:
        story.append(fit_image(ASSETS_DIR / filename, 178 * mm, 70 * mm))
        story.append(paragraph(caption, styles["CaptionArial"]))
        story.append(Spacer(1, 3))
    story.append(PageBreak())

    for filename, caption in [
        ("postings.png", "Figure 4. FI posting ledger showing inventory, GR or IR, vendor, and bank impact."),
        ("controls.png", "Figure 5. 3-way match controls, exception alerts, and quotation comparison."),
    ]:
        story.append(fit_image(ASSETS_DIR / filename, 178 * mm, 76 * mm))
        story.append(paragraph(caption, styles["CaptionArial"]))
        story.append(Spacer(1, 4))

    story.append(paragraph("Future Improvements", styles["SubHeadingArial"]))
    for item in [
        "Add user authentication, approval workflow, and role-based process control.",
        "Introduce searchable document drill-down pages similar to SAP list reports.",
        "Extend vendor evaluation with scoring for price, lead time, quality, and service.",
        "Add charts for spend analytics, blocked invoices, and open liabilities.",
        "Package the solution with deployment automation for easier public hosting and GitHub presentation.",
    ]:
        story.append(bullet_paragraph(item, styles["BodyArial"]))

    story.append(paragraph("Conclusion", styles["SubHeadingArial"]))
    story.append(
        paragraph(
            "The BuildRight P2P Command Center demonstrates how SAP MM procurement concepts can be translated into a functional software project with real business flow, persistent backend logic, and evaluator-friendly outputs. The final solution covers PR, RFQ, quotation, PO, GR, MIRO, and vendor payment while highlighting 3-way match control and MM-FI integration, making it suitable for project submission, demo, and viva discussion.",
            styles["BodyArial"],
        )
    )

    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)


if __name__ == "__main__":
    build_document()
