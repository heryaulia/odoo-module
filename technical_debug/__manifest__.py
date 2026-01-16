# -*- coding: utf-8 -*-
{
    'name': "Technical Debug",

    'summary': "Enhanced field debug tooltips showing module source information",

    'description': """
        Extends Odoo's debug mode field tooltips to display which module(s) a field originates from.
        This makes it easier to track field sources during development and debugging.
    """,

    'author': "hery",
    'website': "https://h3ry.com",

    'category': 'Technical',
    'version': '17.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
    ],
    
    'assets': {
        'web.assets_backend': [
            'technical_debug/static/src/views/fields/field_tooltip.js',
            'technical_debug/static/src/views/fields/field_tooltip.xml',
        ],
    },
    
    'installable': True,
    'application': False,
    'auto_install': False,
}

