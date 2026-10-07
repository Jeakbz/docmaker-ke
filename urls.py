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
        
        Ensure compliance with relevant Kenyan statutes (e.g. Employment Act 2007, Landlord & Tenant Act).
        Format with clear numbered section headings and signature blocks at the bottom.
        """

        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        ai_response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
        )
        
        doc_text = ai_response.text

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
