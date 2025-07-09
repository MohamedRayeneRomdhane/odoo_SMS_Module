import time
import urllib

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class email_template(models.Model):
    _inherit = "mail.template"
    
    sms_template = fields.Boolean('SMS Template')
    mobile_to = fields.Char('To (Mobile)')
    gateway_id = fields.Many2one('sms.tunisiesms', 'SMS Gateway')
    gateway_id = fields.Many2one('sms.tunisiesms', 'SMS Gateway')
    
            
        
    
    
