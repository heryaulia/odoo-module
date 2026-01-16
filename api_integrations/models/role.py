from odoo import models, fields
from odoo.exceptions import ValidationError


class Role(models.Model):
    _name = 'app.role'
    _description = 'Role'

    name = fields.Char(string='Role Name', required=True)
    model_permission_ids = fields.One2many('app.role.model.permission', 'role_id', string='Model Permissions')



    def unlink(self):
        # Check if any users have this role
        users = self.env['app.user'].search_read([('role_ids', 'in', self.ids)], ['id'], limit=1)
        if users:
            raise ValidationError(f"Cannot delete role(s) as they are currently assigned to users.")
        return super(Role, self).unlink()

    # def get_role_by_id(self, id):
    #     app_role_query = """
    #         select 	ar.id,
    #                 ar."name" 
    #         from app_role ar
    #         where ar.id = %s
    #     """

    #     self._cr.execute(app_role_query, (id,))
    #     role_result = self._cr.dictfetchone()

    #     app_role_model_permission_query = """
    #         select 	armp.id,
    #                 im.name,
    #                 armp.can_create,
    #                 armp.can_read,
    #                 armp.can_update,
    #                 armp.can_delete

    #         from app_role_model_permission armp 
    #         left join ir_model im on armp.model_id = im.id 
    #         where armp.role_id = %s
    #     """

    #     self._cr.execute(app_role_model_permission_query, (id,))
    #     model_permissions_result  = self._cr.dictfetchall()

    #     role_result['model_permission'] = model_permissions_result
    #     return role_result

    def get_role_by_id(self, id):
        combined_query = """
            SELECT
                ar.id AS role_id,
                ar."name" AS role_name,
                armp.id AS permission_id,
                im.name AS model_name,
                armp.can_create,
                armp.can_read,
                armp.can_update,
                armp.can_delete
            FROM
                app_role ar
            LEFT JOIN
                app_role_model_permission armp ON ar.id = armp.role_id
            LEFT JOIN
                ir_model im ON armp.model_id = im.id
            WHERE
                ar.id = %s;
        """
        
        self._cr.execute(combined_query, (id,))
        results = self._cr.dictfetchall()
        
        if not results:
            return None
        
        role_data = {
            "id": results[0]['role_id'],
            "name": results[0]['role_name'],
            "model_permission": []
        }
        
        for row in results:
            if row['permission_id']:
                role_data['model_permission'].append({
                    "id": row['permission_id'],
                    "model_name": row['model_name'],
                    "can_create": row['can_create'],
                    "can_read": row['can_read'],
                    "can_update": row['can_update'],
                    "can_delete": row['can_delete']
                })
        
        return role_data


    def get_all_app_role(self):
        combined_query = """
            SELECT
                ar.id AS role_id,
                ar."name" AS role_name,
                armp.id AS permission_id,
                im.name AS model_name,
                armp.can_create,
                armp.can_read,
                armp.can_update,
                armp.can_delete
            FROM
                app_role ar
            LEFT JOIN
                app_role_model_permission armp ON ar.id = armp.role_id
            LEFT JOIN
                ir_model im ON armp.model_id = im.id
            order by ar.id;
        """
        
        self._cr.execute(combined_query)
        results = self._cr.dictfetchall()
        
        if not results:
            return None 
        
        roles = {}
        
        for row in results:
            role_id = row['role_id']
            if role_id not in roles:
                roles[role_id] = {
                    "id": role_id,
                    "name": row['role_name'],
                    "model_permission": []
                }
            
            if row['permission_id']:
                roles[role_id]['model_permission'].append({
                    "id": row['permission_id'],
                    "model_name": row['model_name'],
                    "can_create": row['can_create'],
                    "can_read": row['can_read'],
                    "can_update": row['can_update'],
                    "can_delete": row['can_delete']
                })
        
        return list(roles.values())
