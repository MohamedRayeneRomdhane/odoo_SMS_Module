from odoo import api, fields, models, _
from odoo.exceptions import UserError
import hashlib
import time

class SendCode(models.TransientModel):
    _name = 'sms.tunisiesms.code.send'
    _description = 'Send SMS Code'

    def action_send_code(self):
        self.ensure_one()
        sms_record = self.env['sms.tunisiesms'].browse(self._context.get('active_id'))
        smsto = sms_record.mobile_to or sms_record.partner_id.mobile
        key = hashlib.md5((time.strftime('%Y-%m-%d %H:%M:%S') + (smsto or '')).encode('utf-8')).hexdigest()
        msg = key[0:6]
        sms_record._send_message(smsto, msg)
        sms_record.write({'state': 'waiting', 'code': msg})
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
