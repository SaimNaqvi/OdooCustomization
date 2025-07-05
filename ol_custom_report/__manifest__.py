# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'All Student Report',
    'version':'1.2',
    'sequence':-100,
    'depends':['contacts'],
    'data':['views/ol_menu_item.xml',
            'security/ir.model.access.csv'],
    'installable':True,
    'application':True,
    'auto_install':False,
    'license':'LGPL-3',
}
