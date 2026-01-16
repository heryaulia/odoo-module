# -*- coding: utf-8 -*-
{
    'name': "api_integrations",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],
    
    'external_dependencies': {
        'python': ['jwt', 'passlib'],
    },

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/user_view.xml',
        'views/role_view.xml',
        'views/role_model_permission_view.xml',
        'views/menus.xml',
        'data/data.xml',
    ],
}

