import io
import os
from django.shortcuts import render
from django.http import HttpResponse
from google import genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_document_view(request):
    if request.method == 'POST':
        doc_type = request.POST.get('doc_type', 'General Agreement')
        party_a = request.POST.get('party_a', 'First Party')
        party_b = request.POST.get('party_b', 'Second Party')
        details = request.POST.get('details', '')

        prompt = f"""
You are a legal expert and professional document writer in Kenya.
Generate a structured, formal document for: {doc_type}.
First Party / Issuer: {party_a}
Second Party / Subject: {party_b}
Key Details / Terms / Qualifications: {details}

Ensure compliance with relevant Kenyan laws where applicable (e.g., Employment Act, Land Registration Act, Law of Contract Act).
Format with clear numbered section headings, bold titles, and standard execution/signature blocks at the bottom.
"""

        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        try:
            ai_response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
            )
            doc_text = ai_response.text
        except Exception:
            # Dynamic Fallback Router based on document selection
            doc_lower = doc_type.lower()
            
            if "employment" in doc_lower or "job" in doc_lower:
                doc_text = f"""
EMPLOYMENT CONTRACT

THIS AGREEMENT is made between:
1. THE EMPLOYER: {party_a}
2. THE EMPLOYEE: {party_b}

1. POSITION AND DUTIES
The Employee is engaged in accordance with the Employment Act of Kenya to perform duties and terms outlined as follows: {details}

2. REMUNERATION AND BENEFITS
The Employer agrees to pay the Employee a competitive salary and agreed statutory deductions (NSSF, SHIF/NHIF, PAYE).

3. TERMINATION AND NOTICE
Either party may terminate this employment by giving thirty (30) days written notice or payment in lieu thereof.

IN WITNESS WHEREOF, the parties have executed this Agreement:

EMPLOYER SIGNATURE: ____________________    DATE: ______________
({party_a})

EMPLOYEE SIGNATURE: ____________________    DATE: ______________
({party_b})
"""
            elif "loan" in doc_lower or "lender" in doc_lower or "borrow" in doc_lower:
                doc_text = f"""
LOAN & REPAYMENT AGREEMENT

THIS AGREEMENT is made between:
1. THE LENDER: {party_a}
2. THE BORROWER: {party_b}

1. PRINCIPAL AMOUNT AND TERMS
The Lender agrees to provide financial credit to the Borrower based on the following agreed terms: {details}

2. REPAYMENT AND INTEREST
The Borrower agrees to repay the full principal sum along with any stipulated interest in accordance with the agreed schedule.

3. DEFAULT AND GOVERNING LAW
Failure to remit payments on due dates shall constitute default under the Law of Contract Act of Kenya.

IN WITNESS WHEREOF, the parties have executed this Agreement:

LENDER SIGNATURE: ____________________    DATE: ______________
({party_a})

BORROWER SIGNATURE: ___________________    DATE: ______________
({party_b})
"""
            elif "land" in doc_lower or "property" in doc_lower or "sale" in doc_lower:
                doc_text = f"""
LAND SALE AND TRANSFER AGREEMENT

THIS AGREEMENT is made between:
1. THE VENDOR (SELLER): {party_a}
2. THE PURCHASER (BUYER): {party_b}

1. PROPERTY DESCRIPTION AND PURCHASE PRICE
The Vendor agrees to sell and the Purchaser agrees to buy parcel(s) of land under the Land Registration Act of Kenya as detailed: {details}

2. PAYMENT & STAMP DUTY
The purchase price shall be cleared as agreed, whereupon legal transfer documents and title deeds shall be executed.

IN WITNESS WHEREOF, the parties have executed this Agreement:

VENDOR SIGNATURE: ____________________    DATE: ______________
({party_a})

PURCHASER SIGNATURE: _________________    DATE: ______________
({party_b})
"""
            elif "cv" in doc_lower or "resume" in doc_lower:
                doc_text = f"""
CURRICULUM VITAE (CV)

NAME: {party_a}
TARGET ROLE / PROFESSION: {doc_type}
CONTACT / PREPARED FOR: {party_b}

1. PROFESSIONAL SUMMARY
Dedicated professional seeking to utilize expertise and experience to drive organizational success.

2. KEY QUALIFICATIONS & EXPERIENCE
{details}

3. EDUCATION & SKILLS
* Relevant Degrees, Certifications, and Technical Competencies.
* References available upon request.
"""
            else:
                doc_text = f"""
GENERAL LEGAL AGREEMENT

THIS AGREEMENT is made between:
1. FIRST PARTY: {party_a}
2. SECOND PARTY: {party_b}

1. TERMS AND CONDITIONS
The parties enter into this mutual agreement under the following specified terms: {details}

2. GOVERNING LAW
This agreement is governed by and shall be construed in accordance with the laws of Kenya.

IN WITNESS WHEREOF, the parties set their hands below:

FIRST PARTY SIGNATURE: __________________    DATE: ______________
({party_a})

SECOND PARTY SIGNATURE: _________________    DATE: ______________
({party_b})
"""

        # Create PDF using ReportLab
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']

        story = []
        for line in doc_text.split('\n'):
            if line.strip():
                clean_line = line.replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(clean_line, normal_style))
                story.append(Spacer(1, 6))

        pdf.build(story)
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"{doc_type.replace(' ', '_')}_Kenya.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    return render(request, 'index.html')
