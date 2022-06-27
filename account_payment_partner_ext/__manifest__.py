{
    'name': 'account payment partner ext',

    'version': '14.0.1.0',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'subscription',

    'depends': [

        'sale_subscription',
        'account_payment_mode',

    ],

    'data': [
       
        #'security/security.xml',
        #'security/ir.model.access.csv',
        'views/sale_subscription.xml',
        
    ],
    'installable': True
}

