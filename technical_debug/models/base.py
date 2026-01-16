# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class Base(models.AbstractModel):
    _inherit = 'base'

    def fields_get(self, allfields=None, attributes=None):
        """Override fields_get to add module information to field descriptions"""
        res = super().fields_get(allfields, attributes)
        
        # Only add module info in debug mode to avoid performance impact
        # Check if debug mode is active via session or request
        is_debug = False
        if request and hasattr(request, 'session'):
            is_debug = request.session.debug
        
        if not is_debug:
            return res
        
        # Get field records from ir.model.fields to retrieve module information
        # Use a single batch query instead of searching for each field individually
        IrModelFields = self.env['ir.model.fields'].sudo()
        
        field_names = [fname for fname in res.keys() if fname not in models.MAGIC_COLUMNS]
        
        if field_names:
            # Batch query for all fields at once
            field_records = IrModelFields.search([
                ('model', '=', self._name),
                ('name', 'in', field_names)
            ])
            
            # Create a mapping of field name to modules
            field_modules_map = {fr.name: fr.modules for fr in field_records if fr.modules}
            
            # Add modules information to field descriptions
            for fname, modules in field_modules_map.items():
                if fname in res:
                    res[fname]['modules'] = modules
        
        return res
