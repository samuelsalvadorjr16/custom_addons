# -*- coding: utf-8 -*-
{
    'name': "PCSO Claimant Form",

    'summary': """
        Claimant Form for PCSO
        """,

    'description': """
        An extension of res.partner for PCSO Claimant Form
    """,

    'author': "Moxylus",
    'website': "http://www.moxylus.com/",

    'category': 'Extension',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        #'data/ir_sequence_data.xml',
        'views/claimant_pcso.xml',
        #'views/mrp_repair_pictures.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    #'demo': ['demo/demo.xml',],
}