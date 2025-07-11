from odoo import api, fields, models, _
from odoo.exceptions import UserError
import hashlib
import time

class SendCode(models.TransientModel):
    _name = 'sms.tunisiesms.code.send'
    _description = 'Send SMS Code'

    def action_send_code(self):
        """Send verification code via SMS."""
        self.ensure_one()
        sms_record = self.env['sms.tunisiesms'].browse(self._context.get('active_id'))
        
        # Get mobile number
        mobile_to = sms_record.mobile_to or getattr(sms_record, 'partner_id', None) and sms_record.partner_id.mobile
        
        if not mobile_to:
            raise UserError(_('No mobile number found for sending verification code'))
        
        # Generate verification code
        code_key = hashlib.md5((time.strftime('%Y-%m-%d %H:%M:%S') + mobile_to).encode('utf-8')).hexdigest()
        verification_code = code_key[0:6]
        
        # Create SMS data for sending
        sms_data = type('SMSData', (), {
            'gateway': sms_record,
            'mobile_to': mobile_to,
            'text': f'Your verification code is: {verification_code}',
            'validity': 10,
            'classes1': '1',
            'coding': '1',
            'nostop1': True,
        })()
        
        # Send verification SMS
        try:
            sms_record.send_msg(sms_data)
            sms_record.write({'state': 'waiting', 'code': verification_code})
        except Exception as e:
            raise UserError(_('Failed to send verification code: %s') % str(e))
        
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
