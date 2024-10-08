from project.forms import CreateProjectForm
from invoicing.forms import InvoiceForm


def create_project_form(request):
    """Used to pass the Create Project Form to every page that inherits the base template"""
    return {'createProjectForm': CreateProjectForm()}

def create_invoice_form(request):
    return {'createInvoiceForm' : InvoiceForm()}