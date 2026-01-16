from odoo import models, fields, api

class RoleModelPermission(models.Model):
    _name = 'app.role.model.permission'
    _description = 'Role Model Permission'
    _rec_name = 'name' 

    name = fields.Char('Name', compute='_compute_name', store=True)
    role_id = fields.Many2one('app.role', string='Role', ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    can_create = fields.Boolean(string='Can Create', default=False)
    can_read = fields.Boolean(string='Can Read', default=True)
    can_update = fields.Boolean(string='Can Update', default=False)
    can_delete = fields.Boolean(string='Can Delete', default=False)

    @api.depends('role_id', 'model_id')
    def _compute_name(self):
        for record in self:
            if record.role_id and record.model_id:
                record.name = f"{record.role_id.name} - {record.model_id.name}"