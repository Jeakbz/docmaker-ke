import os
import io
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render
from google import genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_document_view(request):
    if request.method == 'POST':
        doc_type = request.POST.get('doc_type', 'Tenancy Agreement')
        party_a = request.POST.get('party_a', 'Landlord')
        party_b = request.POST.get('party_b', 'Tenant')
        details = request.POST.get('details', '')

        prompt = f"""
You are an advocate of the High Court of Kenya.
Draft a legal document for a: {doc_type}.
First Party: {party_a}
Second Party: {party_b}
Terms & Details: {details}

Ensure compliance with relevant Kenyan statutes (e.g. Employment Act 2007, Land Registration Act).
Format with clear numbered section headings and signature blocks at the bottom.
"""

        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        try:
            ai_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            doc_text = ai_response.text
                except Exception:
            doc_text = f"""
RESIDENTIAL TENANCY AGREEMENT

THIS AGREEMENT is made this day between:

1. THE LANDLORD: {party_a}
2. THE TENANT: {party_b}

1. PREMISES AND TERM
The Landlord agrees to let and the Tenant agrees to take the residential property located in Kenya, subject to the terms and conditions outlined herein.

2. RENT AND FINANCIAL OBLIGATIONS
* Monthly Rent: KES {details} payable in advance on or before the 1st day of each calendar month.
* Utilities: The Tenant shall be responsible for all utility payments including water, electricity, and garbage collection unless explicitly specified otherwise.

3. TENANT COVENANTS
* To keep the interior of the premises in good and clean condition.
* Not to sublet or part with possession of the premises without prior written consent from the Landlord.
* To permit the Landlord or authorized agents to enter and inspect the premises at reasonable times.

4. LANDLORD COVENANTS
* To keep the main structure and exterior of the building in good repair.
* To ensure the Tenant enjoys quiet possession of the premises provided all covenants are fulfilled.

5. TERMINATION
Either party may terminate this agreement by providing a one (1) month written notice to the other party.

IN WITNESS WHEREOF, the parties hereto have executed this Agreement:


LANDLORD SIGNATURE: ____________________    DATE: ______________
{party_a}


TENANT SIGNATURE: ______________________    DATE: ______________
{party_b}
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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', generate_document_view, name='home'),
      ]
