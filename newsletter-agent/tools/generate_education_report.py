#!/usr/bin/env python3
"""
Generate a 5-page PDF report on educational challenges in remote areas
and technology unawareness in Jammu and Kashmir students.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from datetime import datetime

def create_education_report(output_path=".tmp/education_challenges_jk.pdf"):
    """Generate the PDF report on educational challenges."""

    pdf = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=24,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0F0C29'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leading=16
    )

    # PAGE 1: TITLE & INTRODUCTION
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Educational Challenges in Remote Areas", title_style))
    story.append(Paragraph("Technology Unawareness in Jammu and Kashmir Students", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Report prepared on {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(Spacer(1, 0.5*inch))

    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(
        "Jammu and Kashmir, located in the northernmost region of India, encompasses vast geographical areas with "
        "significant remote and hilly terrain. Despite India's technological advancement and digital revolution, "
        "students in remote areas of J&K face unprecedented educational challenges, compounded by limited technology "
        "access and digital literacy. This report examines the multifaceted challenges, underlying causes, and potential "
        "solutions to bridge the digital and educational divide in these regions.",
        body_style
    ))

    story.append(Paragraph("1. Introduction", heading_style))
    story.append(Paragraph(
        "Education is the foundation of societal development and individual empowerment. However, in remote areas of "
        "Jammu and Kashmir, students encounter barriers that significantly hinder their educational progress. The "
        "convergence of geographical isolation, economic constraints, inadequate infrastructure, and limited technology "
        "adoption creates a compounding crisis. While urban India has embraced digital learning, remote areas remain "
        "largely disconnected from technological advancements that could transform education.",
        body_style
    ))

    story.append(Paragraph(
        "The 2020-2021 COVID-19 pandemic exposed these vulnerabilities starkly when schools transitioned to online "
        "learning. Students in remote J&K regions lacked internet connectivity, devices, and digital literacy, "
        "perpetuating educational inequality. This report investigates the root causes and proposes sustainable solutions.",
        body_style
    ))

    # PAGE 2: KEY CHALLENGES
    story.append(PageBreak())

    story.append(Paragraph("2. Key Educational Challenges", heading_style))

    story.append(Paragraph("2.1 Infrastructure Deficit", ParagraphStyle(
        'Subheading',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )))
    story.append(Paragraph(
        "Remote areas of Jammu and Kashmir suffer from inadequate educational infrastructure. Many schools lack "
        "basic facilities such as electricity, potable water, proper classrooms, and sanitation facilities. Limited "
        "transportation connectivity makes it difficult for students to attend school regularly. In winter months, "
        "geographical barriers like snow and landslides further restrict access, forcing prolonged school closures.",
        body_style
    ))

    story.append(Paragraph("2.2 Teacher Shortage and Quality", ParagraphStyle(
        'Subheading',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )))
    story.append(Paragraph(
        "There is a significant shortage of qualified teachers in remote regions. Many schools operate with fewer "
        "teachers than sanctioned strength. Teacher absenteeism is high due to difficult commutes and limited amenities. "
        "Additionally, teachers lack training in modern pedagogical methods and technology integration, limiting their "
        "ability to provide quality education.",
        body_style
    ))

    story.append(Paragraph("2.3 Limited Digital Infrastructure", ParagraphStyle(
        'Subheading',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )))
    story.append(Paragraph(
        "Internet penetration in remote J&K is significantly lower than national averages. Many villages lack mobile "
        "connectivity and broadband access. Where connectivity exists, speeds are insufficient for online learning. "
        "Schools rarely have computers, digital learning resources, or smart classrooms. The digital divide creates "
        "inequitable access to information and learning opportunities.",
        body_style
    ))

    story.append(Paragraph("2.4 Socioeconomic Constraints", ParagraphStyle(
        'Subheading',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )))
    story.append(Paragraph(
        "High poverty rates and agricultural dependence in remote areas drive families to prioritize immediate income "
        "over education. Many students drop out to work in fields or support families. Girls face additional barriers "
        "due to cultural norms and safety concerns, resulting in higher female dropout rates. Economic hardship prevents "
        "families from purchasing devices or paying for private coaching necessary for competitive exams.",
        body_style
    ))

    # PAGE 3: TECHNOLOGY UNAWARENESS
    story.append(PageBreak())

    story.append(Paragraph("3. Technology Unawareness and Digital Literacy", heading_style))

    story.append(Paragraph(
        "Beyond infrastructure, technology unawareness is a critical barrier. Many students and teachers in remote J&K "
        "have never used computers or smartphones for learning. Digital literacy rates are alarmingly low. Students lack "
        "basic skills in using productivity tools, accessing online resources, or navigating digital platforms. Teachers "
        "often resist technology adoption due to unfamiliarity and fear of inadequacy.",
        body_style
    ))

    story.append(Paragraph(
        "Parents in these regions typically have low educational backgrounds and cannot guide children in technology use. "
        "There is widespread skepticism about the relevance of digital skills for rural livelihoods, leading to "
        "underinvestment in technology education. Language barriers compound the problem—most digital content is in English "
        "or Hindi, creating accessibility challenges for local language speakers.",
        body_style
    ))

    story.append(Paragraph("3.1 Impact on Learning Outcomes", ParagraphStyle(
        'Subheading',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )))
    story.append(Paragraph(
        "The absence of technology integration severely impacts learning quality. Students cannot access digital educational "
        "content, e-books, online tutorials, or interactive learning platforms. They miss out on STEM (Science, Technology, "
        "Engineering, Mathematics) education that increasingly requires computational skills. This disadvantage widens the "
        "achievement gap with urban peers and limits career prospects in technology-dependent sectors.",
        body_style
    ))

    story.append(Paragraph("4. Case Study: Ground Realities in J&K Remote Areas", heading_style))

    story.append(Paragraph(
        "A typical remote school in northern Kashmir may have 100+ students but only 2-3 teachers. The school building lacks "
        "electricity and relies on generators during winter. There are no computers or digital devices. Internet connectivity "
        "is a luxury—perhaps only the headmaster's office has a mobile phone with intermittent 2G signal. Students travel "
        "2-3 hours daily on foot to attend school. Many drop out after primary school to engage in agriculture or animal herding.",
        body_style
    ))

    story.append(Paragraph(
        "During COVID-19 lockdowns, these schools completely shut down. Students had no access to online classes. Learning "
        "losses were substantial, particularly in mathematics and languages. Teacher-student contact ceased entirely. Upon "
        "reopening, schools struggled to remediate learning gaps with the same outdated methods. The experience starkly revealed "
        "the inequities in India's education system.",
        body_style
    ))

    # PAGE 4: SOLUTIONS & RECOMMENDATIONS
    story.append(PageBreak())

    story.append(Paragraph("5. Solutions and Recommendations", heading_style))

    story.append(Paragraph("5.1 Infrastructure Development", ParagraphStyle(
        'Subheading',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )))
    story.append(Paragraph(
        "Priority must be given to expanding broadband and mobile connectivity to remote areas through government initiatives "
        "like BharatNet. Solar power systems should be installed in schools to ensure electricity. Every school should have "
        "computers, tablets, and digital learning labs. Adequate transportation support should reduce student dropout rates.",
        body_style
    ))

    story.append(Paragraph("5.2 Teacher Development and Support", ParagraphStyle(
        'Subheading',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )))
    story.append(Paragraph(
        "Comprehensive training programs should equip teachers with technology skills and modern pedagogical methods. Incentive "
        "schemes and accommodation facilities should attract qualified teachers to remote postings. Peer mentoring networks and "
        "online professional development can support continuous learning.",
        body_style
    ))

    story.append(Paragraph("5.3 Digital Literacy Initiatives", ParagraphStyle(
        'Subheading',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )))
    story.append(Paragraph(
        "Structured digital literacy programs for students and adults should be embedded in school curricula. Content should be "
        "available in local languages. Community centers and digital cafes in villages can provide access and training. Partnerships "
        "with NGOs and tech companies can accelerate adoption.",
        body_style
    ))

    story.append(Paragraph("5.4 Content Localization", ParagraphStyle(
        'Subheading',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )))
    story.append(Paragraph(
        "Educational resources, especially for foundational courses, should be available in Kashmiri, Dogri, and other local "
        "languages. Context-relevant examples and case studies should reflect local geography, culture, and livelihoods. This "
        "increases relevance and engagement.",
        body_style
    ))

    story.append(Paragraph("5.5 Inclusive Policies", ParagraphStyle(
        'Subheading',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )))
    story.append(Paragraph(
        "Targeted scholarships and meal schemes should reduce financial barriers. Girls' education initiatives must address safety "
        "and cultural concerns through women teachers and awareness campaigns. Special education provisions for students with "
        "disabilities are essential.",
        body_style
    ))

    # PAGE 5: CONCLUSION
    story.append(PageBreak())

    story.append(Paragraph("6. Conclusion", heading_style))

    story.append(Paragraph(
        "The educational challenges in remote Jammu and Kashmir are deeply rooted in geography, economics, and infrastructure "
        "deficits. Technology unawareness adds another layer of disadvantage, creating a self-perpetuating cycle of inequality. "
        "However, these challenges are not insurmountable. With targeted investments in infrastructure, teacher development, and "
        "digital literacy, combined with policy reforms and community engagement, meaningful change is possible.",
        body_style
    ))

    story.append(Paragraph(
        "Technology, when appropriately adapted and integrated, can be a transformative tool for remote education. Online resources "
        "can compensate for teacher shortages. Digital platforms enable peer learning and collaboration. Mobile technologies can "
        "reach students despite geographical barriers. However, technology is not a panacea—it must be complemented by "
        "infrastructure, teacher empowerment, and socioeconomic support.",
        body_style
    ))

    story.append(Paragraph(
        "The Government of India, Jammu and Kashmir administration, educational institutions, NGOs, and private sector must "
        "collaborate to bridge the educational and digital divide. Achieving Sustainable Development Goal 4 (Quality Education) "
        "requires prioritizing marginalized regions. Every student, regardless of geography, deserves access to quality education "
        "and digital empowerment. The time to act is now.",
        body_style
    ))

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("_______________________________________________", styles['Normal']))
    story.append(Paragraph(f"Report generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))

    # Build PDF
    pdf.build(story)

    print(f"[OK] Education report generated: {output_path}")
    print(f"     Pages: 5")
    print(f"     Topics: Infrastructure, Teachers, Digital Literacy, Case Studies, Solutions")
    print(f"     Focus: Jammu & Kashmir remote areas and technology unawareness")

if __name__ == "__main__":
    create_education_report()
