# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from odoo import fields
from datetime import timedelta
from unittest.mock import patch
from psycopg2 import IntegrityError
from psycopg2.errors import UniqueViolation

class TestAppUser(TransactionCase):

    def setUp(self):
        super(TestAppUser, self).setUp()
        self.role_user = self.env.ref('api_integrations.role_user')
        self.role_admin = self.env.ref('api_integrations.role_admin')
        self.main_company = self.env.ref('base.main_company')
        
        # Create a test user
        self.test_user = self.env['app.user'].create({
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'role_ids': [(4, self.role_user.id)],
            'default_company_id': self.main_company.id,
            'allowed_company_ids': [(4, self.main_company.id)],
        })

    def test_01_password_hashing(self):
        """Test that password is hashed and verification works."""
        self.assertNotEqual(self.test_user.password, 'password123', "Password should be hashed")
        self.assertTrue(self.test_user.check_password('password123'), "Password check should pass")
        self.assertFalse(self.test_user.check_password('wrongpass'), "Password check should fail")
        self.assertFalse(self.test_user.check_password(''), "Empty password check should fail")

    def test_02_unique_email(self):
        """Test email uniqueness constraint."""
        with self.assertRaises((ValidationError, IntegrityError, UniqueViolation)):
            with self.env.cr.savepoint():
                self.env['app.user'].create({
                'name': 'Duplicate Email User',
                'email': 'test@example.com', # Duplicate
                'role_ids': [(4, self.role_user.id)],
                'default_company_id': self.main_company.id,
                'allowed_company_ids': [(4, self.main_company.id)],
            })

    def test_03_create_default_company_constraint(self):
        """Test default company must be in allowed companies."""
        # Create a secondary company
        company_2 = self.env['res.company'].create({
            'name': 'Company 2',
            'fiscalyear_last_day': 31,
            'fiscalyear_last_month': '12',
        })
        
        with self.assertRaises(ValidationError):
            self.env['app.user'].create({
                'name': 'Company Mismatch User',
                'email': 'company@example.com',
                'role_ids': [(4, self.role_user.id)],
                'default_company_id': company_2.id, # Not in allowed ids (which defaults to empty or main if not set properly)
                'allowed_company_ids': [(4, self.main_company.id)],
            })

    def test_04_tokens(self):
        """Test JWT generation and rotation."""
        # Config secret
        self.env['ir.config_parameter'].sudo().set_param('app.user.jwt.secret', 'test_secret')
        
        # Generate
        token = self.test_user.generate_token()
        self.assertTrue(token, "Token should be generated")
        self.assertEqual(self.test_user.auth_token, token, "Token should be stored")
        
        # Rotate
        import time
        time.sleep(2)
        new_token = self.test_user.action_rotate_token()
        self.assertTrue(new_token, "New token generated")
        self.assertNotEqual(token, new_token, "Rotated token should be different (timestamp differs)")

    def test_05_reset_token_lifecycle(self):
        """Test reset token generation, validation, and expiration."""
        # Generate
        token = self.test_user.generate_reset_token()
        self.assertTrue(token)
        self.assertTrue(self.test_user.reset_password_expiration)
        
        # Validate (Valid)
        self.assertTrue(self.test_user.validate_reset_token(token))
        
        # Validate (Invalid Token)
        self.assertFalse(self.test_user.validate_reset_token("wrong_token"))
        
        # Validate (Expired)
        self.test_user.reset_password_expiration = fields.Datetime.now() - timedelta(hours=1)
        self.assertFalse(self.test_user.validate_reset_token(token))
        
        # Reset Logic
        # 1. Regenerate valid token
        token = self.test_user.generate_reset_token()
        # 2. Change password
        self.test_user.change_password("newpassword123")
        # 3. Check token cleared
        self.assertFalse(self.test_user.reset_password_token)
        self.assertFalse(self.test_user.reset_password_expiration)
        self.assertFalse(self.test_user.validate_reset_token(token), "Old token should be invalid")
        self.assertTrue(self.test_user.check_password("newpassword123"))

    def test_06_lifecycle_restrictions(self):
        """Test unlink and copy restrictions."""
        # Unlink with roles -> Should fail
        with self.assertRaises(UserError):
            self.test_user.unlink()
            
        # Unlink without roles -> Should pass
        self.test_user.role_ids = [(5, 0, 0)] # Clear roles
        self.test_user.unlink()
        self.assertFalse(self.test_user.exists())
        
        # Re-create for copy test
        user2 = self.env['app.user'].create({
            'name': 'Copy Test',
            'email': 'copy@example.com',
            'role_ids': [(4, self.role_user.id)],
            'default_company_id': self.main_company.id,
            'allowed_company_ids': [(4, self.main_company.id)],
        })
        
        # Copy -> Should fail
        with self.assertRaises(ValidationError):
            user2.copy()
