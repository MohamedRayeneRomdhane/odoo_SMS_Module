# -*- coding: utf-8 -*-
"""
SMS Access Mixin
================
Common access control methods for SMS-related models to avoid code duplication.
"""

import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class SMSAccessMixin(models.AbstractModel):
    """Mixin providing common SMS access control methods."""
    
    _name = 'sms.access.mixin'
    _description = 'SMS Access Control Mixin'

    def _check_user_sms_access(self):
        """Check if current user has access to SMS functionality."""
        self._cr.execute(
            'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s LIMIT 1',
            (self.env.uid,)
        )
        return bool(self._cr.fetchone())

    def _trigger_access_refresh(self):
        """Trigger comprehensive access refresh for the current user."""
        try:
            # Get the main SMS gateway
            gateway = self.env['sms.tunisiesms'].search([], limit=1)
            if gateway:
                _logger.info("Triggering comprehensive SMS access refresh")
                gateway._ensure_all_users_have_access()
                
                # Additional immediate fix - ensure current user has access
                current_user = self.env.user
                if current_user not in gateway.users_id:
                    _logger.info(f"Adding current user {current_user.name} to SMS gateway")
                    gateway.write({
                        'users_id': [(4, current_user.id)]
                    })
                    
                # Force cache refresh
                self.env.cache.invalidate()
                self.env.registry.clear_caches()
                
        except Exception as e:
            _logger.error(f"Error triggering access refresh: {e}")

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        """Override search to implement shared access for authorized users."""
        # Check if current user has SMS gateway access
        if not self._check_user_sms_access():
            # If user has no SMS access, trigger refresh and check again
            self._trigger_access_refresh()
            if not self._check_user_sms_access():
                # Still no access, return empty recordset
                return super().search([('id', '=', False)], offset, limit, order, count)
        
        # User has SMS access - they can see all records
        return super().search(domain, offset, limit, order, count)
