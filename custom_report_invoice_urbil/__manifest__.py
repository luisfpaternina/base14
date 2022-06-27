# Copyright 2021 Process Control (http://www.processcontrol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Custom Report Invoice Urbil',

    'summary': 'Custom module for Urbil\'s invoices.',

    'version': '14.0.1.0.0',

    'category': 'Invoice',

    'author': 'Luis Felipe Paternina, Process Control',

    'license': 'AGPL-3',
    
    'depends': [
        'account',
        'base',
    ],
    'data': [
        'reports/report_invoice_document.xml',
    ],
}
