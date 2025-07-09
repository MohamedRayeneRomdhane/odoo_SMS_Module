from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VerifyCode(models.TransientModel):
    _name = 'sms.tunisiesms.code.verify'
    _description = 'Verify SMS Code'

    code = fields.Char(string='Verification Code', required=True, help='Enter the verification code that you get in your verification sms')

    def action_verify_code(self):
        self.ensure_one()
        sms_record = self.env['sms.tunisiesms'].browse(self._context.get('active_id'))
        if sms_record.code == self.code:
            sms_record.write({'state': 'confirm'})
        else:
            raise UserError(_('Verification code is incorrect.'))
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
