# -*- coding: utf-8 -*-
{
    'name': "PCSO Prize Claim and Charity",

    'summary': """
        Create Prize claim and Charity Fund
        """,

    'description': """
        PCSO Prize Claim and Charity Fund System
    """,

    'author': "Moxylus",
    'website': "http://www.moxylus.com/",

    'category': 'Extension',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'purchase','hr','mail', 'res_claimant_pcso'],

    # always loaded
    'data': [
        'data/prize_charity_fund_data.xml',
        'data/res_groups.xml',
        'security/voucher_security.xml',
        'wizard/voucher_cancel_return.xml',
        'reports/disbursement_voucher.xml',
        'views/hr_employee.xml',
        'views/prize_charity_configuration.xml',
        'views/request_for_payment.xml',
        'views/account_payment.xml',        
        'views/prize_claim_pcso.xml',        
        'views/account_invoice.xml',
        'views/charity_claim_pcso.xml',
    ],
}