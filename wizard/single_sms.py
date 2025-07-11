import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SingleSMSWizard(models.TransientModel):
    """Single SMS sending wizard for sending SMS to one recipient."""
    
    _name = 'single.tunisiesms'
    _description = 'Single SMS Wizard'

    def _get_default_gateway(self):
        """Get the default SMS gateway."""
        gateway = self.env['sms.tunisiesms'].search([], limit=1)
        return gateway.id if gateway else False

    def _get_default_mobile(self):
        """Get default mobile number from selected partner."""
        if self._context.get('active_model') == 'res.partner':
            partner_ids = self._context.get('active_ids', [])
            if partner_ids:
                partner = self.env['res.partner'].browse(partner_ids[0])
                return partner.mobile or False
        return False

    def send_single_sms(self):
        """Send SMS to a single recipient."""
        if not self.gateway_id:
            raise UserError(_('Please select an SMS gateway'))
        
        if not self.mobile_to:
            raise UserError(_('Please enter a recipient mobile number'))
        
        if not self.text:
            raise UserError(_('Please enter a message'))
        
        try:
            # Create temporary data object with SMS settings from gateway
            sms_data = type('SMSData', (), {
                'gateway': self.gateway_id,
                'mobile_to': self.mobile_to,
                'text': self.text,
                'validity': self.gateway_id.validity,
                'classes1': self.gateway_id.classes,
                'coding': self.gateway_id.coding,
                'nostop1': self.gateway_id.nostop,
            })()
            
            # Send SMS
            self.env['sms.tunisiesms'].send_msg(sms_data)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('SMS Sent'),
                    'message': _('SMS sent successfully to %s') % self.mobile_to,
                    'type': 'success',
                }
            }
            
        except Exception as e:
            raise UserError(_('Failed to send SMS: %s') % str(e))

    # Fields
    gateway_id = fields.Many2one(
        'sms.tunisiesms',
        'SMS Gateway',
        required=True,
        default=_get_default_gateway
    )
    text = fields.Text(
        'SMS Message',
        required=True,
        help='Message content to send'
    )
    mobile_to = fields.Char(
        'Recipient Mobile',
        required=True,
        default=_get_default_mobile,
        help='Mobile number to send SMS to'
    )
