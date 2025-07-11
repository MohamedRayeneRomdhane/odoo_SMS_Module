import urllib
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EmailTemplate(models.Model):
    """Extended email template with SMS functionality."""
    
    _inherit = "mail.template"
    
    sms_template = fields.Boolean(
        'SMS Template',
        help='Enable SMS functionality for this template'
    )
    mobile_to = fields.Char(
        'Mobile Number',
        help='Mobile number for SMS delivery'
    )
    gateway_id = fields.Many2one(
        'sms.tunisiesms',
        'SMS Gateway',
        help='SMS gateway to use for sending'
    )
