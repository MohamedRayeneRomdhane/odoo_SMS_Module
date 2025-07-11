import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)



class MassSMSWizard(models.TransientModel):
    """Mass SMS sending wizard for sending SMS to multiple partners."""
    
    _name = 'part.tunisiesms'
    _description = 'Mass SMS Wizard'

    def _get_default_gateway(self):
        """Get the default SMS gateway."""
        gateway = self.env['sms.tunisiesms'].search([], limit=1)
        return gateway.id if gateway else False
    def _merge_message_template(self, message, record, partner):
        """Merge message template with record data."""
        def replace_placeholder(match):
            expression = str(match.group()[2:-2]).strip()
            try:
                result = eval(expression, {'object': record, 'partner': partner})
                return str(result) if result not in (None, False) else "--------"
            except Exception as e:
                _logger.warning("Template merge error: %s", str(e))
                return "--------"
        
        pattern = re.compile(r'(\[\[.+?\]\])')
        return pattern.sub(replace_placeholder, message)

    def send_mass_sms(self):
        """Send SMS to multiple partners based on selected categories."""
        if not self.gateway:
            raise UserError(_('Please select an SMS gateway'))
        
        if not self.category_id:
            raise UserError(_('Please select at least one partner category'))
        
        # Get all partners from selected categories
        partner_ids = []
        for category in self.category_id:
            category_partners = self.env['res.partner'].search([
                ('category_id', '=', category.id)
            ])
            partner_ids.extend(category_partners.ids)
        
        # Remove duplicates
        partner_ids = list(dict.fromkeys(partner_ids))
        
        if not partner_ids:
            raise UserError(_('No partners found in the selected categories'))
        
        # Send SMS to each partner
        sent_count = 0
        skipped_count = 0
        
        for partner in self.env['res.partner'].browse(partner_ids):
            if not partner.mobile:
                skipped_count += 1
                continue
            
            try:
                # Prepare SMS data
                sms_data = self._prepare_sms_data(partner)
                
                # Send SMS
                self.env['sms.tunisiesms'].send_msg(sms_data)
                sent_count += 1
                
            except Exception as e:
                _logger.error("Failed to send SMS to partner %s: %s", partner.name, str(e))
                skipped_count += 1
        
        # Show result notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Mass SMS Sent'),
                'message': _('SMS sent to %d partners, %d skipped') % (sent_count, skipped_count),
                'type': 'success',
            }
        }

    def _prepare_sms_data(self, partner):
        """Prepare SMS data object for sending."""
        return type('SMSData', (), {
            'gateway': self.gateway,
            'mobile_to': partner.mobile,
            'text': self.text,
            'validity': self.gateway.validity,
            'classes1': self.gateway.classes,
            'coding': self.gateway.coding,
            'nostop1': self.gateway.nostop,
        })()

    # Fields
    gateway = fields.Many2one(
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
    
    # Partner Categories
    category_id = fields.Many2many(
        'res.partner.category',
        column1='part_sms_id',
        column2='category_id',
        string='Partner Categories',
        help='Select partner categories to send SMS to'
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
