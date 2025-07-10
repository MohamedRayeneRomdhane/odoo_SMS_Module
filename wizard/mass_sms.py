from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import re



class part_sms(models.TransientModel):
    _name = 'part.tunisiesms'
    _description = 'Part SMS'

    def _default_get_gateway(self):
        sms_obj = self.env['sms.tunisiesms']
        gateway_ids = sms_obj.search([], limit=1)
        return gateway_ids and gateway_ids[0] or False

    @api.onchange('gateway')
    def onchange_gateway_mass(self):
        if not self.gateway:
            return
        gateway = self.gateway
        self.validity = gateway.validity
        self.classes = gateway.classes
        self.deferred = gateway.deferred
        self.priority = gateway.priority
        self.coding = gateway.coding
        self.tag = gateway.tag
        # Convert boolean to string for selection field
        self.nostop = '1' if gateway.nostop else '0'

    def _merge_message(self, message, object, partner):
        def merge(match):
            exp = str(match.group()[2: -2]).strip()
            result = eval(exp, {'object': object, 'partner': partner})
            if result in (None, False):
                return str("--------")
            return str(result)
        com = re.compile('(\[\[.+?\]\])')
        msg = com.sub(merge, message)
        return msg

    def sms_mass_send(self):
        partner_ids = []
        for categ in self.category_id:
            rels = self.env['res.partner'].search([('category_id', '=', categ.id)])
            partner_ids.extend(rels.ids)
        partner_ids = list(dict.fromkeys(partner_ids))
        client_obj = self.env['sms.tunisiesms']
        partner_obj = self.env['res.partner']
        if not self.gateway:
            raise UserError(_('You can only select one partner'))
        for partner in partner_obj.browse(partner_ids):
            self.mobile_to = partner.mobile

            # Set classes1 and nostop1 for queue compatibility
            self.classes1 = self.classes
            self.nostop1 = True if self.nostop == '1' else False

            # Log all details before sending
            _logger = self.env['ir.logging']
            print("=== SMS MASS SEND DETAILS ===")
            print(f"API Gateway URL: {self.gateway.url}")
            print(f"API Key: {self.gateway.key_url_params}")
            print(f"Sender: {self.gateway.sender_url_params}")
            print(f"Phone Number: {self.mobile_to}")
            print(f"Message: {self.text}")
            print("=============================")

            client_obj.send_msg(self)
        return True

    def send_single_sms(self):
        if not self.gateway:
            raise UserError(_('You must select a gateway.'))
        if not self.mobile_to:
            raise UserError(_('You must enter a recipient mobile number.'))
        if not self.text:
            raise UserError(_('You must enter a message.'))
        client_obj = self.env['sms.tunisiesms']
        # Log all details before sending
        print("=== SMS SINGLE SEND DETAILS ===")
        print(f"API Gateway URL: {self.gateway.url}")
        print(f"API Key: {self.gateway.key_url_params}")
        print(f"Sender: {self.gateway.sender_url_params}")
        print(f"Phone Number: {self.mobile_to}")
        print(f"Message: {self.text}")
        print("=============================")
        client_obj.send_msg(self)
        return True

    gateway = fields.Many2one('sms.tunisiesms', 'SMS Gateway', default=_default_get_gateway)
    text = fields.Text('Text', required=True)
    mobile_to = fields.Char('Recipient Mobile')
    classes1 = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit'),
    ], 'Class')
    nostop1 = fields.Boolean('NoStop')
    validity = fields.Integer('Validity',
            help='The maximum time -in minute(s)- before the message is dropped')
    classes = fields.Selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit'),
            ], 'Class',
            help='The sms class: flash(0),phone display(1),SIM(2),toolkit(3)')
    deferred = fields.Integer('Deferred',
            help='The time -in minute(s)- to wait before sending the message')
    priority = fields.Selection([
                ('0', '0'),
                ('1', '1'),
                ('2', '2'),
                ('3', '3')
            ], 'Priority', help='The priority of the message')
    coding = fields.Selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ], 'Coding', help='The sms coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char('Tag',  help='An optional tag')

    category_id = fields.Many2many('res.partner.category', column1='part_sms_id',
                                    column2='category_id', string='Tags test')

    nostop = fields.Selection([
                ('0', '0'),
                ('1', '1')
            ], 'NoStop',
            help='Do not display STOP clause in the message, this requires that this is not an advertising message')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
