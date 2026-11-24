import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_oos_assay_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0f172a'),
        alignment=0,
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0284c7'),
        alignment=0,
    )
    
    header_right_style = ParagraphStyle(
        'HeaderRight',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#64748b'),
        alignment=2,
    )

    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
    )

    alert_style = ParagraphStyle(
        'Alert',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#991b1b'),
    )

    story = []

    # Document Header Table
    header_data = [
        [
            Paragraph("<b>AIVOA PHARMACEUTICAL CHEMICALS CORP.</b><br/>Active Pharmaceutical Ingredient (API) Manufacturing Facility<br/>Quality Assurance & Regulatory Compliance Directorate", subtitle_style),
            Paragraph("<b>FORM: QMS-DEV-FORM-04</b><br/>Revision: 06<br/>ICH Q7 §12 & 21 CFR Part 211", header_right_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[360, 180])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceBefore=4, spaceAfter=8))

    story.append(Paragraph("OUT-OF-SPECIFICATION (OOS) DEVIATION INVESTIGATION REPORT", title_style))
    story.append(Spacer(1, 6))

    # Summary Meta Table
    meta_data = [
        [
            Paragraph("<b>Deviation Number:</b>", body_style), Paragraph("<b>DEV-2026-0914</b>", body_style),
            Paragraph("<b>Initial Severity:</b>", body_style), Paragraph("<font color='#b91c1c'><b>CRITICAL</b></font>", body_style)
        ],
        [
            Paragraph("<b>Target API Product:</b>", body_style), Paragraph("Atorvastatin Calcium Trihydrate API", body_style),
            Paragraph("<b>Batch / Lot Number:</b>", body_style), Paragraph("<b>BAT-ATC-2026-0914</b>", body_style)
        ],
        [
            Paragraph("<b>Manufacturing Stage:</b>", body_style), Paragraph("Reaction & Controlled Crystallization", body_style),
            Paragraph("<b>Equipment ID Tag:</b>", body_style), Paragraph("<b>REACT-CR-01</b> (3000L Glass-Lined)", body_style)
        ],
        [
            Paragraph("<b>Incident Date / Time:</b>", body_style), Paragraph("2026-11-20 03:45:00 UTC", body_style),
            Paragraph("<b>Investigation Status:</b>", body_style), Paragraph("<b>Under Review</b>", body_style)
        ],
    ]
    meta_table = Table(meta_data, colWidths=[120, 150, 120, 150])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # Section 1: Deviation Event Description
    story.append(Paragraph("1. Description of Deviation Event & Analytical OOS Result", h2_style))
    desc_p1 = (
        "During commercial manufacturing of Atorvastatin Calcium Trihydrate batch BAT-ATC-2026-0914 in Suite 3, "
        "the crystallization step in 3000L glass-lined reactor REACT-CR-01 suffered an uncontrolled thermal excursion. "
        "According to the Batch Manufacturing Record (BMR Page 42 of 68), the batch recipe mandates controlled linear cooling "
        "from 65.0°C down to 20.0°C ± 2.0°C over 6 hours under continuous 45 RPM dual-impeller agitation. "
        "At 03:45 UTC, cooling jacket control valve TCV-104 failed open due to pneumatic positioner signal loss, causing rapid chilling "
        "followed by operator bypass manipulation that overheated the jacket slurry to 38.5°C for 52 minutes."
    )
    story.append(Paragraph(desc_p1, body_style))
    story.append(Spacer(1, 4))
    
    desc_p2 = (
        "Following wet milling and vacuum tray drying, QC Analytical Laboratory received final release sample QC-2026-914-A. "
        "High Performance Liquid Chromatography (HPLC) assay analysis on column C-18 (5 um, 250 x 4.6 mm) yielded an Assay of <b>94.2% w/w</b> "
        "(anhydrous basis), which is Out-Of-Specification against the ICH Q7 validated specification limit of <b>98.0% - 102.0% w/w</b>. "
        "The OOS was confirmed upon repeat duplicate injection by a second analyst."
    )
    story.append(Paragraph(desc_p2, body_style))
    story.append(Spacer(1, 8))

    # Section 2: Immediate Containment Actions
    story.append(Paragraph("2. Immediate Containment & Quarantine Actions", h2_style))
    containment_text = (
        "1. Batch BAT-ATC-2026-0914 (Total 420.5 kg dry weight packaged in double polyethylene bags in fiber drums) "
        "was immediately placed under QA Yellow Quarantine Tag #Q-914 in Secure Quarantine Bay 3.<br/>"
        "2. Reactor REACT-CR-01 was locked out and tagged out (LOTO #LOTO-CR01-11) pending engineering inspection of pneumatic valve TCV-104.<br/>"
        "3. Downstream dispensing and packaging operations for Line 3 were halted."
    )
    story.append(Paragraph(containment_text, alert_style))
    story.append(Spacer(1, 8))

    # Section 3: Technical Hypotheses
    story.append(Paragraph("3. Preliminary Technical Hypotheses", h2_style))
    hypo_text = (
        "• <b>Machine/Instrumentation:</b> Proportional pneumatic positioner on TCV-104 suffered diaphragm tear or 4-20mA DCS control loop signal drop.<br/>"
        "• <b>Method/Process:</b> Thermal spike to 38.5°C induced polymorphic transformation and lactonization/solvolysis degradation during crystallization.<br/>"
        "• <b>Measurement:</b> Potential HPLC system baseline integration error or standard preparation weight discrepancy."
    )
    story.append(Paragraph(hypo_text, body_style))
    story.append(Spacer(1, 8))

    # Section 4: Notice of Missing Investigation Evidence (Intentionally flagged gaps)
    story.append(Paragraph("4. Technical Evidence Audit Status (ICH Q7 §12 & §14)", h2_style))
    gap_notice = (
        "<b>NOTE FOR QA INVESTIGATOR:</b> The following mandatory physical and analytical records are currently <b>MISSING</b> from the initial deviation intake package:<br/>"
        "• <i>Missing Item 1:</i> HPLC Raw Integration Files, Chromatograms, and System Suitability sequence run for sample QC-2026-914-A (required to rule out chromatographic baseline drift or peak tailing).<br/>"
        "• <i>Missing Item 2:</i> Calibration Certificate and Maintenance History for Reactor Temperature Transmitter TT-104 (last calibration overdue by 14 days per instrument tag).<br/>"
        "• <i>Missing Item 3:</i> Mother Liquor Mass Balance & Crystallization Yield Analysis (necessary to verify if missing active ingredient partition dissolved into filtrate vs decomposed)."
    )
    story.append(Paragraph(gap_notice, body_style))
    story.append(Spacer(1, 12))

    # Signatures Table
    sig_data = [
        [Paragraph("<b>Investigator:</b> J. Ramirez, Production Supervisor", body_style), Paragraph("<b>Signature / Date:</b> J. Ramirez (2026-11-20)", body_style)],
        [Paragraph("<b>QA Reviewer:</b> Dr. S. Mehta, Lead QA Auditor", body_style), Paragraph("<b>Status:</b> PENDING QA ROOT CAUSE VERIFICATION", alert_style)]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sig_table)

    doc.build(story)
    print(f"Generated PDF: {output_path}")

def create_incident_email(output_path: str):
    content = """From: qc-analytical-lead@pharma-api.com
To: qa-compliance@pharma-api.com, chemical-operations@pharma-api.com, engineering-support@pharma-api.com
Date: 2026-11-22 09:30:00
Subject: CRITICAL DEVIATION: DEV-2026-1102 - Related Substance Impurity D Spike in Losartan Potassium Lot LOS-2026-1102

Dear QA Compliance & Operations Teams,

During final release testing of Losartan Potassium API lot LOS-2026-1102 produced on Line 3, QC chromatography reported an unexpected Out-of-Specification spike for Related Substance Impurity D (Dimer Adduct).

1. DEVIATION METADATA:
- Deviation Number: DEV-2026-1102
- Severity: Critical
- API Product Name: Losartan Potassium USP
- Batch / Lot Number: LOT-LOS-2026-1102
- Equipment ID Tag: FBD-02 (Fluid Bed Dryer Line 3)
- Manufacturing Stage: Final Drying & Solvent Evaporation
- Incident Date: 2026-11-22 08:15:00

2. EVENT DESCRIPTION:
HPLC purity testing performed under QC Protocol #SOP-QC-441 revealed Impurity D at 0.38% w/w. The validated release specification is NMT 0.15% w/w.
Batch processing records indicate this batch was dried in Fluid Bed Dryer FBD-02. Notably, during the final recrystallization wash step prior to drying, operations switched to a new solvent lot of Isopropanol (Supplier: ChemSupply Inc., Lot #CS-IPA-991), replacing our primary supplier lot.

3. IMMEDIATE CONTAINMENT:
Lot LOT-LOS-2026-1102 (310 kg bulk API) has been placed under QA Yellow Quarantine Tag #Q-1102 in Warehouse Bay 4. Solvent storage tank TK-IPA-03 has been locked out to prevent charging to subsequent batches.

4. MISSING TECHNICAL RECORDS NOTED BY QC:
- Critical Gap 1: Missing Confirmatory Testing & Certificate of Analysis (CoA) for raw material Isopropanol Lot #CS-IPA-991 (water content by Karl Fischer and peroxide value were not independently verified prior to vessel charging).
- Critical Gap 2: Missing FBD-02 inlet air HEPA filter differential pressure log and continuous moisture trap log (could not confirm drying chamber relative humidity during final 4 hours).
- Critical Gap 3: Missing Gas Chromatography (GC) head-space residual solvent chromatogram data for the affected batch.

Please initiate the RCA StateGraph workflow and notify Qualified Person (QP).

Best regards,
Dr. Elena Rostova
QC Analytical Laboratory Lead
AIVOA Active Pharmaceutical Ingredients Facility"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Generated Email Text: {output_path}")

def create_shift_handover_log(output_path: str):
    content = """SHIFT B TO SHIFT C HANDOVER LOG & INCIDENT REPORT
================================================================================
Date/Time: 2026-11-23 18:00:00 UTC
Shift Supervisor: Mark Jenkins, Chemical Operations
Area: API Wet Cake Isolation Suite 4
================================================================================

1. DEVIATION IDENTIFICATION:
Deviation Number: DEV-2026-0520
Severity: Major
API Product Name: Clopidogrel Bisulfate Form I
Batch / Lot Number: BAT-CLP-2026-0520
Equipment Tag: CF-03 (Inverting Filter Centrifuge)
Manufacturing Stage: Wet Cake Isolation & Cake Washing
Incident Date: 2026-11-23 16:20:00

2. OPERATOR INCIDENT CHRONOLOGY:
- 16:05 UTC: Operator loaded crystallization slurry batch BAT-CLP-2026-0520 into Inverting Filter Centrifuge CF-03.
- 16:20 UTC: During the high-speed mother liquor spin (1200 RPM), operator observed the Nitrogen inerting blanket pressure transmitter PT-402 plunge from normal 50 mbar positive pressure down to 8 mbar (alarm threshold < 15 mbar).
- 16:22 UTC: Heavy vibration detected on drive shaft; minor hydrocarbon smoke smell noticed near the upper mechanical seal housing.
- 16:30 UTC: Operator performed emergency stop (E-Stop). Shift maintenance technician arrived and found the mechanical seal silicone-elastomer gasket degraded and leaking barrier fluid (mineral oil flush).
- 16:45 UTC: Technician replaced the mechanical seal gasket using a spare from workshop inventory (Part #GSK-SIL-88) without waiting for an Engineering Change Control (CC) form or QA engineering sign-off.
- 17:15 UTC: Centrifugation was restarted and 280 kg wet cake cake discharged into transfer bin TB-04.

3. IMMEDIATE CONTAINMENT / QUARANTINE:
- Wet cake transfer bin TB-04 tagged with QA Yellow Hold Tag #Q-0520.
- Centrifuge CF-03 placed on engineering hold.
- Sample pulled for visual particulate and lubricant contamination inspection.

4. INVESTIGATION GAPS / MISSING GMP RECORDS:
- Critical Gap 1: Missing Approved Engineering Change Control (CC) and Maintenance Work Order for the emergency gasket replacement on Centrifuge CF-03.
- Critical Gap 2: Missing Food/Pharma-Grade Lubricant Compatibility & Leachables Certificate for replacement seal gasket Part #GSK-SIL-88.
- Critical Gap 3: Missing Nitrogen header manifold pressure log and oxygen sensor analyzer (AO-102) calibration log during the pressure drop window.

Handed over to Shift C Lead (D. Vance) for QA Deviation initiation."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Generated Shift Log: {output_path}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_data")
    os.makedirs(out_dir, exist_ok=True)
    
    create_oos_assay_pdf(os.path.join(out_dir, "deviation_oos_assay.pdf"))
    create_incident_email(os.path.join(out_dir, "incident_email_impurity.txt"))
    create_shift_handover_log(os.path.join(out_dir, "shift_handover_log.txt"))
