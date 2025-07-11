import urllib
import urllib.parse
from datetime import datetime
import json
import logging

import jxmlease
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    from SOAPpy import WSDL
except ImportError:
    _logger.warning("SOAPpy not installed. Install it with: pip install SOAPpy")


class TunisieSMS(models.Model):
    """SMS Gateway configuration and management model."""
    
    _name = 'sms.tunisiesms'
    _description = 'Tunisie SMS Gateway'

    # Basic Configuration
    name = fields.Char(
        'Gateway Name', 
        default='TUNISIESMS',
        readonly=True, 
        required=True
    )
    url = fields.Char(
        'Gateway URL',
        required=True,
        readonly=True,
        default='https://api.l2t.io/tn/v0/api/api.aspx',
        help='Base URL for SMS messages'
    )
    
    # Gateway Properties and History
    property_ids = fields.One2many(
        'sms.tunisiesms.parms',
        'gateway_id',
        string='Parameters'
    )
    history_line = fields.One2many(
        'sms.tunisiesms.history',
        'gateway_id',
        string='History'
    )
    
    # API Configuration
    method = fields.Selection([
        ('http', 'HTTP Method'),
        ('smpp', 'SMPP Method')
    ], 'API Method', readonly=True, default='http')
    
    state = fields.Selection([
        ('new', 'Not Verified'),
        ('waiting', 'Waiting for Verification'),
        ('confirm', 'Verified'),
    ], 'Gateway Status', default='new', readonly=True)
    
    # Access Control
    users_id = fields.Many2many(
        'res.users',
        'res_smsserver_group_rel',
        'sid',
        'uid',
        string='Users Allowed'
    )
    
    # Message Configuration
    code = fields.Char('Verification Code')
    body = fields.Text(
        'Message',
        help="Default message template for SMS notifications"
    )
    validity = fields.Integer(
        'Validity',
        help='Maximum time in minutes before message is dropped',
        default=10
    )
    classes = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit')
    ], 'Class', help='SMS class: flash(0), phone display(1), SIM(2), toolkit(3)', default='1')
    
    deferred = fields.Integer(
        'Deferred',
        help='Time in minutes to wait before sending message',
        default=0
    )
    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
    ], 'Priority', help='Message priority level')
    
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
    ], 'Coding', help='SMS coding: 1 for 7 bit or 2 for unicode')
    
    tag = fields.Char('Tag', help='Optional tag for message tracking')
    nostop = fields.Boolean(
        'NoStop',
        help='Do not display STOP clause (non-advertising messages only)',
        default=True
    )
    char_limit = fields.Boolean('Character Limit', default=True)

    # Order Status SMS Templates
    order_draft_sms = fields.Text('Order Draft SMS Template')
    status_order_draft = fields.Boolean('Enable Order Draft SMS', default=True)
    
    order_sent_sms = fields.Text('Order Sent SMS Template')
    status_order_sent = fields.Boolean('Enable Order Sent SMS', default=True)
    
    order_waiting_sms = fields.Text('Order Waiting SMS Template')
    status_order_waiting = fields.Boolean('Enable Order Waiting SMS', default=True)
    
    order_sale_sms = fields.Text('Order Sale SMS Template')
    status_order_sale = fields.Boolean('Enable Order Sale SMS', default=True)
    
    order_done_sms = fields.Text('Order Done SMS Template')
    status_order_done = fields.Boolean('Enable Order Done SMS', default=True)
    
    order_cancel_sms = fields.Text('Order Cancel SMS Template')
    status_order_cancel = fields.Boolean('Enable Order Cancel SMS', default=True)
    
    # Partner SMS Templates
    res_partner_sms_create = fields.Text('New Contact SMS Template')
    status_res_partner_create = fields.Boolean('Enable New Contact SMS', default=True)
    
    # URL Parameters
    mobile_url_params = fields.Char('Mobile URL Parameter', default='mobile')
    sms_url_params = fields.Char('SMS URL Parameter', default='sms')
    fct_url_params = fields.Char('Function URL Parameter', default='fct')
    sender_url_params = fields.Char('Sender URL Parameter')
    key_url_params = fields.Text('API Key Parameter')
    
    # Error Management
    code_error_status = fields.One2many(
        'sms.tunisiesms.code.error',
        'gateway_id',
        string='Error Codes',
        readonly=True
    )
    
    # Notification Labels
    label_order = fields.Char(
        'Order Label',
        required=True,
        readonly=True,
        default='Please mention these fields in your text: %STATE% %DATE% %NAME%'
    )

    def _check_permissions(self):
        """Check if current user has permission to use SMS gateway."""
        self._cr.execute(
            'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s LIMIT 1',
            (self.env.uid,)
        )
        return bool(self._cr.fetchone())

    def _prepare_tunisiesms_queue(self, data, name):
        """Prepare SMS queue data for message sending."""
        return {
            'name': name,
            'gateway_id': data.gateway.id,
            'state': 'draft',
            'mobile': data.mobile_to,
            'msg': data.text,
            'validity': getattr(data, 'validity', self.validity),
            'classes1': getattr(data, 'classes1', self.classes),
            'coding': getattr(data, 'coding', self.coding),
            'nostop1': bool(getattr(data, 'nostop1', self.nostop)),
        }

    def send_msg(self, data):
        """Send SMS message through the configured gateway."""
        if not data.gateway:
            raise UserError(_('No SMS gateway configured'))
            
        gateway = data.gateway
        
        # Check permissions
        if not self._check_permissions():
            raise UserError(_('You do not have permission to use gateway: %s') % gateway.name)
        
        _logger.info("Sending SMS via %s to %s", gateway.name, data.mobile_to)
        
        try:
            if gateway.method == 'http':
                self._send_http_sms(data, gateway)
            elif gateway.method == 'smpp':
                self._send_smpp_sms(data, gateway)
            else:
                raise UserError(_('Unsupported SMS method: %s') % gateway.method)
                
            # Create queue entry for tracking
            queue_vals = self._prepare_tunisiesms_queue(data, gateway.url)
            self.env['sms.tunisiesms.queue'].create(queue_vals)
            
        except Exception as e:
            _logger.error("SMS send failed: %s", str(e))
            # Log failure in history
            self._create_history_entry(
                gateway, data, '', 'error', '', str(e)
            )
            raise UserError(_('Failed to send SMS: %s') % str(e))
        
        return True

        
    def _check_queue(self):
        """Process SMS queue and send pending messages."""
        queue_obj = self.env['sms.tunisiesms.queue']
        
        # Get pending messages
        pending_sms = queue_obj.search([
            ('state', 'not in', ['send', 'sending'])
        ], limit=30)
        
        if not pending_sms:
            return True
            
        # Mark as sending
        pending_sms.write({'state': 'sending'})
        
        error_ids = []
        sent_ids = []
        
        for sms in pending_sms:
            try:
                # Check character limit
                if sms.gateway_id.char_limit and len(sms.msg) > 160:
                    error_ids.append(sms.id)
                    continue
                
                # Process based on method
                if sms.gateway_id.method == 'http':
                    self._process_http_queue_item(sms)
                elif sms.gateway_id.method == 'smpp':
                    self._process_smpp_queue_item(sms)
                else:
                    _logger.error("Unsupported SMS method: %s", sms.gateway_id.method)
                    error_ids.append(sms.id)
                    continue
                    
                sent_ids.append(sms.id)
                
            except Exception as e:
                _logger.error("Failed to process SMS queue item %s: %s", sms.id, str(e))
                error_ids.append(sms.id)
        
        # Update status
        if sent_ids:
            queue_obj.browse(sent_ids).write({'state': 'send'})
        
        if error_ids:
            queue_obj.browse(error_ids).write({
                'state': 'error',
                'error': 'SMS processing failed'
            })
        
        return True

   
    
    @api.model
    def get_tunisiesms_action(self):
        """Get action for Tunisie SMS form view."""
        gateway = self.sudo().search([("id", "=", 1)], limit=1)
        
        return {
            "type": "ir.actions.act_window",
            "context": self.env.context,
            "res_model": "sms.tunisiesms",
            "view_type": "form",
            "view_mode": "form",
            "view_id": self.env.ref("odoo_SMS_Module.sms_tunisiesms_form").id,
            "res_id": gateway.id if gateway else False,
            "target": "inline",
        }

    def update_sms_client(self):
        """Update SMS client configuration."""
        for record in self:
            _logger.info("Updating SMS client configuration for: %s", record.name)
            # Add any specific update logic here
        return True

    def _send_http_sms(self, data, gateway):
        """Send SMS via HTTP method."""
        params = {
            'mobile': data.mobile_to,
            'sms': data.text,
            'fct': 'sms',
            'sender': gateway.sender_url_params,
            'key': gateway.key_url_params
        }
        
        query_string = urllib.parse.urlencode(params)
        full_url = f"{gateway.url}?{query_string}"
        
        try:
            response = requests.get(full_url, timeout=30)
            response.raise_for_status()
            
            # Parse response
            message_id, status_code, status_mobile, status_msg = self._parse_sms_response(response.text)
            
            # Create history entry
            self._create_history_entry(
                gateway, data, message_id, status_code, status_mobile, status_msg
            )
            
        except Exception as e:
            _logger.error("HTTP SMS send failed: %s", str(e))
            raise

    def _send_smpp_sms(self, data, gateway):
        """Send SMS via SMPP method."""
        # Extract SMPP parameters
        login = password = sender = account = None
        
        for param in gateway.property_ids:
            if param.type == 'user':
                login = param.value
            elif param.type == 'password':
                password = param.value
            elif param.type == 'sender':
                sender = param.value
            elif param.type == 'sms':
                account = param.value
        
        if not all([login, password, sender, account]):
            raise UserError(_('SMPP parameters not properly configured'))
        
        try:
            soap = WSDL.Proxy(gateway.url)
            
            # Handle message encoding
            message = data.text
            if getattr(data, 'coding', '1') == '2':
                message = message.encode('utf-8')
            
            # Send via SOAP
            result = soap.telephonySmsUserSend(
                str(login), str(password), str(account), str(sender),
                str(data.mobile_to), message,
                int(getattr(data, 'validity', gateway.validity)),
                int(getattr(data, 'classes1', gateway.classes)),
                int(getattr(data, 'deferred', gateway.deferred)),
                int(getattr(data, 'priority', 0)),
                int(getattr(data, 'coding', 1)),
                str(gateway.tag or ''),
                int(getattr(data, 'nostop1', gateway.nostop))
            )
            
            # Log success
            self._create_history_entry(
                gateway, data, str(result), 'success', data.mobile_to, 'SMPP sent'
            )
            
        except Exception as e:
            raise UserError(_('SMPP send failed: %s') % str(e))
    
    def _parse_sms_response(self, response_text):
        """Parse SMS gateway XML response."""
        try:
            root = jxmlease.parse(response_text)
            return (
                root['response']['status']['message_id'].get_cdata(),
                root['response']['status']['status_code'].get_cdata(),
                root['response']['status']['status_mobile'].get_cdata(),
                root['response']['status']['status_msg'].get_cdata()
            )
        except Exception as e:
            _logger.warning("Failed to parse SMS response: %s", str(e))
            return '', 'parse_error', '', str(e)
    
    def _create_history_entry(self, gateway, data, message_id, status_code, status_mobile, status_msg):
        """Create SMS history entry."""
        history_name = _('SMS Sent') if status_code == '200' else _('SMS Send Error')
        
        self.env['sms.tunisiesms.history'].create({
            'name': history_name,
            'gateway_id': gateway.id,
            'sms': data.text,
            'to': data.mobile_to,
            'message_id': message_id,
            'status_code': status_code,
            'status_mobile': status_mobile,
            'status_msg': status_msg,
            'date_create': datetime.now(),
            'user_id': self.env.uid
        })

class SMSQueue(models.Model):
    """SMS Queue for managing pending SMS messages."""
    
    _name = 'sms.tunisiesms.queue'
    _description = 'SMS Queue'
    _order = 'date_create desc'

    name = fields.Text(
        'SMS Request',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    msg = fields.Text(
        'SMS Text',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    mobile = fields.Char(
        'Mobile Number',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    gateway_id = fields.Many2one(
        'sms.tunisiesms',
        'SMS Gateway',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    state = fields.Selection([
        ('draft', 'Queued'),
        ('sending', 'Sending'),
        ('send', 'Sent'),
        ('error', 'Error'),
    ], 'Status', readonly=True, default='draft')
    
    error = fields.Text(
        'Error Message',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    date_create = fields.Datetime(
        'Created Date',
        readonly=True,
        default=fields.Datetime.now
    )
    
    # SMS Parameters
    validity = fields.Integer(
        'Validity (minutes)',
        help='Maximum time before message is dropped'
    )
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], 'Priority', help='Message priority level')
    
    classes1 = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit')
    ], 'Class', help='SMS class: flash(0), phone display(1), SIM(2), toolkit(3)')
    
    deferred = fields.Integer(
        'Deferred (minutes)',
        help='Time to wait before sending message',
        default=0
    )
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
    ], 'Coding', help='SMS encoding: 7 bit or Unicode')
    
    tag = fields.Char('Tag', help='Optional message tag')
    nostop1 = fields.Boolean(
        'No Stop Clause',
        help='Do not display STOP clause for non-advertising messages'
    )


class SMSGatewayParameters(models.Model):
    """SMS Gateway Parameters for configuring API connections."""
    
    _name = 'sms.tunisiesms.parms'
    _description = 'SMS Gateway Parameters'

    name = fields.Char(
        'Parameter Name',
        required=True,
        help='Name of the parameter for the API URL'
    )
    value = fields.Char(
        'Parameter Value',
        required=True,
        help='Value associated with the parameter'
    )
    gateway_id = fields.Many2one(
        'sms.tunisiesms',
        'SMS Gateway',
        required=True,
        ondelete='cascade'
    )
    type = fields.Selection([
        ('user', 'Username'),
        ('password', 'Password'),
        ('sender', 'Sender Name'),
        ('to', 'Recipient Number'),
        ('sms', 'SMS Message'),
        ('extra', 'Extra Information')
    ], 'Parameter Type', required=True, help='Parameter type for API integration')

class SMSHistory(models.Model):
    """SMS History for tracking sent messages and their status."""
    
    _name = 'sms.tunisiesms.history'
    _description = 'SMS History'
    _order = 'date_create desc'

    name = fields.Char(
        'Description',
        required=True,
        readonly=True
    )
    date_create = fields.Datetime(
        'Date Created',
        readonly=True,
        default=fields.Datetime.now
    )
    user_id = fields.Many2one(
        'res.users',
        'User',
        readonly=True,
        default=lambda self: self.env.uid
    )
    gateway_id = fields.Many2one(
        'sms.tunisiesms',
        'SMS Gateway',
        readonly=True,
        ondelete='set null'
    )
    to = fields.Char(
        'Recipient Number',
        readonly=True
    )
    sms = fields.Text(
        'SMS Content',
        readonly=True
    )
    
    # API Response Fields
    message_id = fields.Char('Message ID', readonly=True)
    status_code = fields.Char('Status Code', readonly=True)
    status_mobile = fields.Char('Mobile Status', readonly=True)
    status_msg = fields.Char('Status Message', readonly=True)
    dlr_msg = fields.Char('Delivery Report', readonly=True)
 
    def get_dlr_status(self):
        """Get delivery status for SMS messages."""
        # Get pending delivery reports
        pending_history = self.search([
            ('dlr_msg', '=', False),
            ('message_id', '!=', False),
            ('message_id', '!=', '1')
        ], order='date_create desc', limit=30)
        
        for history_item in pending_history:
            try:
                self._fetch_delivery_status(history_item)
            except Exception as e:
                _logger.error("Failed to fetch DLR for message %s: %s", 
                             history_item.message_id, str(e))
        
        return True
    
    def _fetch_delivery_status(self, history_item):
        """Fetch delivery status for a single message."""
        if not history_item.gateway_id or not history_item.message_id:
            return
            
        gateway = history_item.gateway_id
        params = {
            'fct': 'dlr',
            'key': gateway.key_url_params,
            'msg_id': history_item.message_id
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{gateway.url}?{query_string}"
        
        try:
            response = urllib.request.urlopen(url, timeout=30).read()
            root = jxmlease.parse(response)
            
            acknowledgement = root['acknowledgement']['message']['acknowledgement'].get_cdata()
            history_item.write({'dlr_msg': acknowledgement})
            
        except Exception as e:
            _logger.error("DLR fetch failed for message %s: %s", 
                         history_item.message_id, str(e))  

class PartnerSMSSend(models.Model):
    """Partner SMS Send model for sending SMS to specific partners."""
    
    _name = "partner.tunisiesms.send"
    _description = 'Partner SMS Send'

    @api.model
    def _get_default_mobile(self):
        """Get default mobile number from selected partner."""
        partner_ids = self._context.get('active_ids', [])
        
        if not partner_ids:
            return False
            
        if len(partner_ids) > 1:
            raise UserError(_('You can only select one partner'))
        
        partner = self.env['res.partner'].browse(partner_ids[0])
        return partner.mobile or False

    @api.model
    def _get_default_gateway(self):
        """Get default SMS gateway."""
        gateway = self.env['sms.tunisiesms'].search([], limit=1)
        return gateway.id if gateway else False

    @api.onchange('gateway_id')
    def _onchange_gateway(self):
        """Update SMS parameters when gateway changes."""
        if not self.gateway_id:
            return
            
        gateway = self.gateway_id
        self.update({
            'validity': gateway.validity,
            'classes1': gateway.classes,
            'deferred': gateway.deferred,
            'priority': gateway.priority,
            'coding': gateway.coding,
            'tag': gateway.tag,
            'nostop1': gateway.nostop,
        })

    # Basic Fields
    mobile_to = fields.Char(
        'Recipient Mobile',
        required=True,
        default=_get_default_mobile
    )
    text = fields.Text(
        'SMS Message',
        required=True
    )
    gateway = fields.Many2one(
        'sms.tunisiesms',
        'SMS Gateway',
        required=True,
        default=_get_default_gateway
    )
    
    # API Fields (for compatibility)
    app_id = fields.Char('API ID')
    user = fields.Char('Login')
    password = fields.Char('Password')
    
    # SMS Parameters
    validity = fields.Integer(
        'Validity (minutes)',
        help='Maximum time before message is dropped'
    )
    classes1 = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit')
    ], 'Class', help='SMS class: flash(0), phone display(1), SIM(2), toolkit(3)')
    
    deferred = fields.Integer(
        'Deferred (minutes)',
        help='Time to wait before sending message',
        default=0
    )
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], 'Priority', help='Message priority level')
    
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
    ], 'Coding', help='SMS encoding: 7 bit or Unicode')
    
    tag = fields.Char('Tag', help='Optional message tag')
    nostop1 = fields.Boolean(
        'No Stop Clause',
        help='Do not display STOP clause for non-advertising messages'
    )
    
    def sms_send(self):
        """Send SMS to selected partner."""
        if not self.gateway:
            raise UserError(_('Please select an SMS gateway'))
        
        if not self.mobile_to:
            raise UserError(_('Please enter a recipient mobile number'))
        
        if not self.text:
            raise UserError(_('Please enter a message'))
        
        # Send SMS
        gateway_obj = self.env['sms.tunisiesms']
        gateway_obj.send_msg(self)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('SMS Sent'),
                'message': _('SMS sent successfully to %s') % self.mobile_to,
                'type': 'success',
            }
        }
     
class SaleOrderSMS(models.Model):
    """Sale Order SMS integration for automatic SMS notifications."""
    
    _inherit = 'sale.order'

    # SMS Status Tracking
    tunisie_sms_status = fields.Integer(
        'SMS Status',
        default=0,
        help='0: Pending, 1: Sent, 2: No Mobile, 3: Disabled, 4: Skipped'
    )
    tunisie_sms_send_date = fields.Datetime('SMS Send Date')
    tunisie_sms_write_date = fields.Datetime('SMS Write Date')
    tunisie_sms_msisdn = fields.Char('SMS Mobile Number')

    def process_order_sms_notifications(self):
        """Process SMS notifications for orders with status 0."""
        orders_to_process = self.search([('tunisie_sms_status', '=', 0)])
        
        if not orders_to_process:
            return True
            
        sms_gateway = self.env['sms.tunisiesms'].search([('id', '=', 1)], limit=1)
        
        if not sms_gateway:
            _logger.warning("No SMS gateway configured")
            return True
        
        current_time = fields.Datetime.now()
        
        for order in orders_to_process:
            try:
                self._process_single_order_sms(order, sms_gateway, current_time)
            except Exception as e:
                _logger.error("Failed to process SMS for order %s: %s", order.name, str(e))
        
        return True
    
    def _process_single_order_sms(self, order, sms_gateway, current_time):
        """Process SMS notification for a single order."""
        partner_mobile = order.partner_id.mobile
        
        if not partner_mobile:
            order.update({
                'tunisie_sms_status': 2,  # No mobile
                'tunisie_sms_send_date': current_time,
                'tunisie_sms_write_date': current_time,
            })
            return
        
        # Get SMS template and permission based on order state
        sms_template, send_permission = self._get_order_sms_config(order.state, sms_gateway)
        
        if not send_permission:
            order.update({
                'tunisie_sms_status': 3,  # Disabled
                'tunisie_sms_send_date': current_time,
                'tunisie_sms_write_date': current_time,
                'tunisie_sms_msisdn': partner_mobile,
            })
            return
        
        # Replace template variables
        final_message = self._replace_order_variables(sms_template, order)
        
        # Create SMS data
        sms_data = self.env['partner.tunisiesms.send'].create({
            'gateway': sms_gateway.id,
            'mobile_to': partner_mobile,
            'text': final_message
        })
        
        # Send SMS
        try:
            self.env['sms.tunisiesms'].send_msg(sms_data)
            order.update({
                'tunisie_sms_status': 1,  # Sent
                'tunisie_sms_send_date': current_time,
                'tunisie_sms_write_date': current_time,
                'tunisie_sms_msisdn': partner_mobile,
            })
        except Exception as e:
            _logger.error("Failed to send SMS for order %s: %s", order.name, str(e))
            order.update({
                'tunisie_sms_status': 3,  # Error
                'tunisie_sms_send_date': current_time,
                'tunisie_sms_write_date': current_time,
                'tunisie_sms_msisdn': partner_mobile,
            })
    
    def _get_order_sms_config(self, order_state, sms_gateway):
        """Get SMS template and permission for order state."""
        state_config = {
            'draft': (sms_gateway.order_draft_sms, sms_gateway.status_order_draft),
            'sent': (sms_gateway.order_sent_sms, sms_gateway.status_order_sent),
            'waiting': (sms_gateway.order_waiting_sms, sms_gateway.status_order_waiting),
            'sale': (sms_gateway.order_sale_sms, sms_gateway.status_order_sale),
            'done': (sms_gateway.order_done_sms, sms_gateway.status_order_done),
            'cancel': (sms_gateway.order_cancel_sms, sms_gateway.status_order_cancel),
        }
        
        return state_config.get(order_state, ('', False))
    
    def _replace_order_variables(self, template, order):
        """Replace template variables with order data."""
        if not template:
            return ''
        
        # Use the utility method for replacing variables
        return self.env['sms.tunisiesms.generic'].replace_with_table_attribute(
            template, 'sale_order', order
        )


class ResPartnerSMS(models.Model):
    """Partner SMS integration for automatic SMS notifications."""
    
    _inherit = 'res.partner'

    # SMS Status Tracking
    tunisie_sms_status = fields.Integer(
        'SMS Status',
        default=0,
        help='0: Pending, 1: Sent, 2: No Mobile, 3: Disabled, 4: Skipped'
    )
    tunisie_sms_send_date = fields.Datetime('SMS Send Date')
    tunisie_sms_write_date = fields.Datetime('SMS Write Date')

    def process_partner_sms_notifications(self):
        """Process SMS notifications for new partners."""
        partners_to_process = self.search([('tunisie_sms_status', '=', 0)])
        
        if not partners_to_process:
            return True
        
        sms_gateway = self.env['sms.tunisiesms'].search([('id', '=', 1)], limit=1)
        
        if not sms_gateway:
            _logger.warning("No SMS gateway configured")
            return True
        
        # Get administrator mobile for notifications
        admin_partner = self.search([('name', '=', 'Administrator')], limit=1)
        admin_mobile = admin_partner.mobile if admin_partner else None
        
        if not admin_mobile:
            _logger.warning("Administrator mobile not configured")
            return True
        
        current_time = fields.Datetime.now()
        
        for partner in partners_to_process:
            try:
                self._process_single_partner_sms(partner, sms_gateway, admin_mobile, current_time)
            except Exception as e:
                _logger.error("Failed to process SMS for partner %s: %s", partner.name, str(e))
        
        return True
    
    def _process_single_partner_sms(self, partner, sms_gateway, admin_mobile, current_time):
        """Process SMS notification for a single partner."""
        if not sms_gateway.status_res_partner_create:
            partner.update({
                'tunisie_sms_status': 3,  # Disabled
                'tunisie_sms_send_date': current_time,
                'tunisie_sms_write_date': current_time,
            })
            return
        
        # Get SMS template
        sms_template = sms_gateway.res_partner_sms_create
        
        if not sms_template:
            partner.update({
                'tunisie_sms_status': 3,  # No template
                'tunisie_sms_send_date': current_time,
                'tunisie_sms_write_date': current_time,
            })
            return
        
        # Replace template variables
        final_message = self.env['sms.tunisiesms.generic'].replace_with_table_attribute(
            sms_template, 'res_partner', partner
        )
        
        # Create SMS data
        sms_data = self.env['partner.tunisiesms.send'].create({
            'gateway': sms_gateway.id,
            'mobile_to': admin_mobile,
            'text': final_message
        })
        
        # Send SMS
        try:
            self.env['sms.tunisiesms'].send_msg(sms_data)
            partner.update({
                'tunisie_sms_status': 1,  # Sent
                'tunisie_sms_send_date': current_time,
                'tunisie_sms_write_date': current_time,
            })
        except Exception as e:
            _logger.error("Failed to send SMS for partner %s: %s", partner.name, str(e))
            partner.update({
                'tunisie_sms_status': 3,  # Error
                'tunisie_sms_send_date': current_time,
                'tunisie_sms_write_date': current_time,
            })

class SMSErrorCode(models.Model):
    """SMS Error Code management for tracking API response codes."""
    
    _name = 'sms.tunisiesms.code.error'
    _description = 'SMS Error Codes'

    code = fields.Char('Error Code', required=True)
    libelle = fields.Char('Description', required=True)
    gateway_id = fields.Many2one(
        'sms.tunisiesms',
        'SMS Gateway',
        required=True,
        ondelete='cascade'
    )

    @api.model
    def populate_error_codes(self):
        """Populate error codes with default values."""
        default_codes = [
            {"code": "200", "description": "Success"},
            {"code": "400", "description": "Bad Request - Missing ID"},
            {"code": "401", "description": "Unauthorized - Invalid ID"},
            {"code": "402", "description": "Payment Required - Insufficient Credit"},
            {"code": "403", "description": "Forbidden - Module Not Authorized"},
            {"code": "420", "description": "Daily Quota Exceeded"},
            {"code": "430", "description": "Missing Content"},
            {"code": "431", "description": "Missing Destination"},
            {"code": "440", "description": "Content Too Long"},
            {"code": "441", "description": "Destination Not Authorized"},
            {"code": "442", "description": "Sender Not Authorized"},
            {"code": "500", "description": "Internal Server Error"},
            {"code": "501", "description": "Invalid Date"},
            {"code": "502", "description": "Invalid Time"}
        ]
        
        # Get the first gateway
        gateway = self.env['sms.tunisiesms'].search([], limit=1)
        
        if not gateway:
            _logger.warning("No SMS gateway found for error code population")
            return True
        
        # Check if codes need to be updated
        existing_codes = self.search([('gateway_id', '=', gateway.id)])
        
        if len(existing_codes) != len(default_codes):
            # Remove existing codes and recreate
            existing_codes.unlink()
            
            for code_data in default_codes:
                self.create({
                    'code': code_data['code'],
                    'libelle': code_data['description'],
                    'gateway_id': gateway.id
                })
        
        return True

class TunisieSMSGeneric(models.Model):
    """Generic utilities for SMS text replacement and processing."""
    
    _name = 'sms.tunisiesms.generic'
    _description = 'Tunisie SMS Generic Utilities'

    def replace_with_table_attribute(self, text_to_change, table_name, record):
        """Replace template variables with database field values."""
        if not text_to_change or not table_name or not record:
            return text_to_change or ''
        
        try:
            # Get table columns
            query = "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
            self._cr.execute(query, (table_name,))
            columns = self._cr.fetchall()
            
            # Replace each column placeholder
            for column in columns:
                column_name = column[0]
                placeholder = f"%{column_name}%"
                
                try:
                    # Get field value from record
                    field_value = record[column_name]
                    
                    # Convert to string, handling special cases
                    if field_value is None or field_value is False:
                        replacement = ''
                    elif hasattr(field_value, 'name'):
                        # Handle Many2one fields
                        replacement = field_value.name
                    elif isinstance(field_value, (list, tuple)):
                        # Handle One2many/Many2many fields
                        replacement = ', '.join(str(item) for item in field_value)
                    else:
                        replacement = str(field_value)
                    
                    text_to_change = text_to_change.replace(placeholder, replacement)
                    
                except (KeyError, AttributeError):
                    # Skip if field doesn't exist or is not accessible
                    continue
                    
        except Exception as e:
            _logger.error("Error in template replacement: %s", str(e))
            
        return text_to_change

class TunisieSMSSetup(models.Model):
    """Setup utilities for initializing SMS module data and triggers."""
    
    _name = 'sms.tunisiesms.setup'
    _description = 'Tunisie SMS Setup'
    
    @api.model
    def initialize_error_codes(self):
        """Initialize SMS error codes in the database."""
        error_codes_data = [
            {"status": "200", "message": "Success - Message sent"},
            {"status": "400", "message": "Bad Request - Missing ID"},
            {"status": "401", "message": "Unauthorized - Invalid ID"},
            {"status": "402", "message": "Payment Required - Insufficient credit"},
            {"status": "403", "message": "Forbidden - Module not authorized"},
            {"status": "420", "message": "Daily quota exceeded"},
            {"status": "430", "message": "Missing content"},
            {"status": "431", "message": "Missing destination"},
            {"status": "440", "message": "Content too long"},
            {"status": "441", "message": "Destination not authorized"},
            {"status": "442", "message": "Sender not authorized"},
            {"status": "500", "message": "Internal server error"},
            {"status": "501", "message": "Invalid date"},
            {"status": "502", "message": "Invalid time"}
        ]

        error_code_obj = self.env['sms.tunisiesms.code.error']
        existing_codes = error_code_obj.search([])
        
        # Update codes if count doesn't match
        if len(existing_codes) != len(error_codes_data):
            existing_codes.unlink()
            
            for code_data in error_codes_data:
                error_code_obj.create({
                    'code': code_data["status"],
                    'libelle': code_data["message"],
                    'gateway_id': 1  # Default gateway
                })
        
        return True

    @api.model
    def reset_order_sms_status(self):
        """Reset order SMS status from 0 to 4 (skip processing)."""
        order_obj = self.env['sale.order']
        
        # Check if any orders have status 4 (already processed)
        processed_orders = order_obj.search([('tunisie_sms_status', '=', 4)])
        
        if not processed_orders:
            # Reset pending orders to skip status
            pending_orders = order_obj.search([('tunisie_sms_status', '=', 0)])
            pending_orders.write({'tunisie_sms_status': 4})
        
        return True

    @api.model
    def reset_partner_sms_status(self):
        """Reset partner SMS status from 0 to 4 (skip processing)."""
        partner_obj = self.env['res.partner']
        
        # Check if any partners have status 4 (already processed)
        processed_partners = partner_obj.search([('tunisie_sms_status', '=', 4)])
        
        if not processed_partners:
            # Reset pending partners to skip status
            pending_partners = partner_obj.search([('tunisie_sms_status', '=', 0)])
            pending_partners.write({'tunisie_sms_status': 4})
        
        return True

    @api.model
    def create_default_gateway(self):
        """Create default SMS gateway if none exists."""
        gateway_obj = self.env['sms.tunisiesms']
        
        existing_gateways = gateway_obj.search([])
        if not existing_gateways:
            gateway_obj.create({'name': 'TUNISIESMS'})
        
        return True

    @api.model
    def create_sale_order_trigger(self):
        """Create database trigger for sale order SMS notifications."""
        try:
            # Create the trigger function
            self._cr.execute("""
                CREATE OR REPLACE FUNCTION trigger_sale_order_sms_reset()
                RETURNS TRIGGER
                LANGUAGE plpgsql
                AS $$
                BEGIN
                    -- Reset SMS status when order state changes
                    IF NEW.state IS DISTINCT FROM OLD.state THEN
                        NEW.tunisie_sms_status = 0;
                    END IF;
                    
                    RETURN NEW;
                END;
                $$;
            """)
            
            # Create the trigger
            self._cr.execute("""
                DROP TRIGGER IF EXISTS tr_sale_order_sms_reset ON sale_order;
                CREATE TRIGGER tr_sale_order_sms_reset
                    BEFORE UPDATE ON sale_order
                    FOR EACH ROW
                    WHEN (NEW.state IS DISTINCT FROM OLD.state)
                    EXECUTE FUNCTION trigger_sale_order_sms_reset();
            """)
            
            _logger.info("Sale order SMS trigger created successfully")
            
        except Exception as e:
            _logger.error("Failed to create sale order SMS trigger: %s", str(e))
        
        return True

    def _process_http_queue_item(self, sms):
        """Process HTTP SMS queue item."""
        try:
            response = urllib.request.urlopen(sms.name, timeout=30).read()
            message_id, status_code, status_mobile, status_msg = self._parse_sms_response(response)
            
            # Create history entry
            self.env['sms.tunisiesms.history'].create({
                'name': _('SMS Sent'),
                'gateway_id': sms.gateway_id.id,
                'sms': sms.msg,
                'to': sms.mobile,
                'message_id': message_id,
                'status_code': status_code,
                'status_mobile': status_mobile,
                'status_msg': status_msg,
                'date_create': datetime.now()
            })
            
        except Exception as e:
            raise UserError(_('HTTP queue processing failed: %s') % str(e))
    
    def _process_smpp_queue_item(self, sms):
        """Process SMPP SMS queue item."""
        # Extract SMPP parameters
        login = password = sender = account = None
        
        for param in sms.gateway_id.property_ids:
            if param.type == 'user':
                login = param.value
            elif param.type == 'password':
                password = param.value
            elif param.type == 'sender':
                sender = param.value
            elif param.type == 'sms':
                account = param.value
        
        if not all([login, password, sender, account]):
            raise UserError(_('SMPP parameters not configured'))
        
        try:
            soap = WSDL.Proxy(sms.gateway_id.url)
            
            # Handle message encoding
            message = sms.msg
            if sms.coding == '2':
                message = message.encode('utf-8')
            
            # Send via SOAP
            result = soap.telephonySmsUserSend(
                str(login), str(password), str(account), str(sender),
                str(sms.mobile), message,
                int(sms.validity or 0),
                int(sms.classes1 or 1),
                int(sms.deferred or 0),
                int(sms.priority or 0),
                int(sms.coding or 1),
                str(sms.gateway_id.tag or ''),
                int(sms.gateway_id.nostop or 0)
            )
            
            # Create history entry
            self.env['sms.tunisiesms.history'].create({
                'name': _('SMS Sent'),
                'gateway_id': sms.gateway_id.id,
                'sms': sms.msg,
                'to': sms.mobile,
                'message_id': str(result),
                'status_code': 'success',
                'status_mobile': sms.mobile,
                'status_msg': 'SMPP sent successfully',
                'date_create': datetime.now()
            })
            
        except Exception as e:
            raise UserError(_('SMPP queue processing failed: %s') % str(e))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: