from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html_escape
from .jwt_utils import generate_jwt
import logging

try:
    from passlib.context import CryptContext
except ImportError:
    CryptContext = None

_logger = logging.getLogger(__name__)


class AppUser(models.Model):
    _name = 'app.user'
    _description = 'App User'
    _inherit = ['mail.thread', 'image.mixin']


    _crypt_context = CryptContext(schemes=['pbkdf2_sha512', 'plaintext'], deprecated="auto") if CryptContext else None

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(string='Active', default=True)
    email = fields.Char(required=True, tracking=True, index=True)
    allowed_company_ids = fields.Many2many('res.company', string='Allowed Company', required=True, tracking=True)
    default_company_id = fields.Many2one('res.company', string='Default Company', required=True, tracking=True, domain="[('id', 'in', allowed_company_ids)]")
    password = fields.Char(invisible=True, copy=False)
    role_ids = fields.Many2many('app.role', string='Roles', required=True, copy=False)
    auth_token = fields.Char(string='Auth Token', invisible=True, copy=False, index=True)

    reset_password_token = fields.Char(copy=False)
    reset_password_expiration = fields.Datetime(copy=False)

    token_version = fields.Integer(default=0)















    _sql_constraints = [
        ('email_unique', 'unique(email)', 'Email must be unique!'),
    ]

    def action_force_relogin(self):
        self.token_version += 1

    def _hash_password(self, password):
        if not self._crypt_context:
            import hashlib
            import base64
            return base64.b64encode(hashlib.sha256(password.encode('utf-8')).digest()).decode('utf-8')
        return self._crypt_context.hash(password)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('password'):
                vals['password'] = self._hash_password(vals['password'])
        return super(AppUser, self).create(vals_list)

    def write(self, vals):
        if vals.get('password'):
            vals['password'] = self._hash_password(vals['password'])
        return super(AppUser, self).write(vals)

    def action_archive(self):
        self.sudo().write({
            'active': False,
            'auth_token': False
        })
    
    def action_active(self):
        self.sudo().write({'active': True})

    def check_password(self, password):
        self.ensure_one()
        if not self.password:
            return False
        if not self._crypt_context:
             # Fallback for compatibility if passlib missing (though unlikely in Odoo)
            import hashlib
            import base64
            return self.password == base64.b64encode(hashlib.sha256(password.encode('utf-8')).digest()).decode('utf-8')
        try:
            return self._crypt_context.verify(password, self.password)
        except ValueError:
            return False

    def _get_jwt_secret(self):
        params = self.env['ir.config_parameter'].sudo()
        secret = params.get_param('app.user.jwt.secret')
        if not secret:
            import secrets
            secret = secrets.token_urlsafe(32)
            params.set_param('app.user.jwt.secret', secret)
        return secret

    def generate_token(self):
        self.ensure_one()
        token_payload = {"user_id": self.id, "name": self.name}
        secret = self._get_jwt_secret()
        token = generate_jwt(token_payload, secret_key=secret)
        self.auth_token = token
        return token

    def generate_reset_token(self):
        import secrets
        from datetime import timedelta
        self.ensure_one()
        token = secrets.token_urlsafe(32)
        self.write({
            'reset_password_token': token,
            'reset_password_expiration': fields.Datetime.now() + timedelta(hours=24)
        })
        return token

    def validate_reset_token(self, token):
        self.ensure_one()
        if not token or token != self.reset_password_token:
            return False
        if fields.Datetime.now() > self.reset_password_expiration:
            return False
        return True

    def action_rotate_token(self):
        return self.generate_token()

    def action_open_wizard_change_password(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Password Atrium',
            'res_model': 'wizard.change.password.atrium.user',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    def change_password(self, new_password):
        self.ensure_one()
        self.write({
            'password': self._hash_password(new_password),
            'reset_password_token': False,
            'reset_password_expiration': False
        })
        self.generate_token()
        self._message_log(body=_('Password Has Been Changed'))

    def unlink(self):
        if self.filtered(lambda u: u.role_ids):
             raise UserError(('You cannot delete User that have roles.'))
        return super(AppUser, self).unlink()

    
    @api.constrains('default_company_id')
    def _check_default_company(self):
        if self.default_company_id not in self.allowed_company_ids:
            raise ValidationError(f'Default Company must be in Allowed company list')


    def copy(self, default=None):
        raise ValidationError(f'You cannot duplicate user.')



