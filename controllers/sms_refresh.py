from odoo import http, _
from odoo.http import request
import json

class SMSRefreshController(http.Controller):
    
    @http.route('/sms/refresh_access', type='json', auth='user')
    def refresh_access(self):
        """Web controller to refresh SMS access for current user."""
        try:
            # Get SMS gateway and refresh access
            gateway = request.env['sms.tunisiesms'].search([], limit=1)
            if gateway:
                gateway._ensure_all_users_have_access()
                
                # Clear session cache
                request.session.logout(keep_db=True)
                request.session.authenticate(request.session.db, request.session.uid, request.session.password)
                
                return {
                    'success': True,
                    'message': _('SMS access refreshed successfully')
                }
            else:
                return {
                    'success': False,
                    'message': _('No SMS gateway found')
                }
        except Exception as e:
            return {
                'success': False,
                'message': _('Failed to refresh SMS access: %s') % str(e)
            }
    
    @http.route('/sms/check_access', type='json', auth='user')
    def check_access(self):
        """Check if current user has SMS access."""
        try:
            # Check direct access via res_smsserver_group_rel
            request.env.cr.execute(
                'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s LIMIT 1',
                (request.env.uid,)
            )
            has_access = bool(request.env.cr.fetchone())
            
            return {
                'has_access': has_access,
                'user_id': request.env.uid,
                'user_name': request.env.user.name
            }
        except Exception as e:
            return {
                'has_access': False,
                'error': str(e)
            }
