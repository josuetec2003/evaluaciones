from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings

from xhtml2pdf import pisa
import os

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def render_to_pdf_utf8(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def render_to_pdf_and_save(template_src, fname, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    reports_folder = os.path.join(settings.BASE_DIR, 'reports')
    file = open(reports_folder + fname, "w+b")

    pdf = pisa.CreatePDF(html.encode("utf-8"), dest=file, encoding='utf-8')

    if pdf:
        return True
    else:
        return False
