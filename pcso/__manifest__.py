# -*- coding: utf-8 -*-
{
    'name': "pcso",

    'summary': """
       PCSO Customizations
       """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Moxylus",
    'website': "http://www.moxylus.ph",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'custom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/sales_team_security.xml',
        # 'data/ir_sequence_data.xml',
        'data/pcso_transaction_type_data.xml',
        'data/pcso_branch_data.xml',
        'views/pcso_transaction_type_view.xml',
        'views/pcso_budget_allocation_view.xml',
        'views/pcso_branch_view.xml',
        'views/pcso_assistance_view.xml',
        'views/pcso_specific_assistance_view.xml',
        'views/pcso_transaction_view.xml',
        'views/pcso_api_error_matrix_view.xml',
        'views/account_view.xml',
        'views/pcso_menu_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}