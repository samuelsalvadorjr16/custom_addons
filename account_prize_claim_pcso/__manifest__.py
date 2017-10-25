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
    'depends': ['base', 'account', 'res_claimant_pcso'],

    # always loaded
    'data': [
        'data/prize_charity_fund_data.xml',
        'data/res_groups.xml',
        'reports/disbursement_voucher.xml',
        'views/account_payment.xml',
        'views/prize_charity_configuration.xml',
        'views/prize_claim_pcso.xml',
    ],
}