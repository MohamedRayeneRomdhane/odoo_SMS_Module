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
        string='Authorized Users',
        help='Users authorized to access this SMS gateway'
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

    # Order Status SMS Templates & Triggers
    order_draft_sms = fields.Text(
        'Draft Order SMS Template',
        help='Template for SMS sent when order is in draft state. Use %field_name% for variables.'
    )
    status_order_draft = fields.Boolean(
        'Draft Order SMS Trigger',
        default=True,
        help='Enable automatic SMS when order is in draft state'
    )

    order_sent_sms = fields.Text(
        'Quotation Sent SMS Template',
        help='Template for SMS sent when quotation is sent to customer'
    )
    status_order_sent = fields.Boolean(
        'Quotation Sent SMS Trigger',
        default=True,
        help='Enable automatic SMS when quotation is sent'
    )

    order_waiting_sms = fields.Text(
        'Waiting Approval SMS Template',
        help='Template for SMS sent when order is waiting for approval'
    )
    status_order_waiting = fields.Boolean(
        'Waiting Approval SMS Trigger',
        default=True,
        help='Enable automatic SMS when order is waiting'
    )

    order_sale_sms = fields.Text(
        'Order Confirmed SMS Template',
        help='Template for SMS sent when order is confirmed (sale state)'
    )
    status_order_sale = fields.Boolean(
        'Order Confirmed SMS Trigger',
        default=True,
        help='Enable automatic SMS when order is confirmed'
    )

    order_done_sms = fields.Text(
        'Order Completed SMS Template',
        help='Template for SMS sent when order is completed/delivered'
    )
    status_order_done = fields.Boolean(
        'Order Completed SMS Trigger',
        default=True,
        help='Enable automatic SMS when order is completed'
    )

    order_cancel_sms = fields.Text(
        'Order Cancelled SMS Template',
        help='Template for SMS sent when order is cancelled'
    )
    status_order_cancel = fields.Boolean(
        'Order Cancelled SMS Trigger',
        default=True,
        help='Enable automatic SMS when order is cancelled'
    )

    # Partner SMS Templates & Triggers
    res_partner_sms_create = fields.Text(
        'New Contact Notification Template',
        help='Template for admin notification when new contact/customer is created'
    )
    status_res_partner_create = fields.Boolean(
        'New Contact SMS Trigger',
        default=True,
        help='Enable admin SMS notification when new contact is created'
    )

    # Automatic SMS Trigger Configuration
    auto_sms_enabled = fields.Boolean(
        'Enable Automatic SMS System',
        default=True,
        help='Master switch: Enable/disable all automatic SMS triggers globally'
    )
    auto_sms_on_create = fields.Boolean(
        'Trigger SMS on Order Creation',
        default=True,
        help='Send SMS automatically when new orders are created (draft state)'
    )
    auto_sms_on_status_change = fields.Boolean(
        'Trigger SMS on Status Changes',
        default=True,
        help='Send SMS automatically when order status changes between states'
    )

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

    # Template Variables Help
    label_order = fields.Text(
        'Template Variables Reference',
        required=True,
        readonly=True,
        default='''Common variables you can use in SMS templates:
• %name% = Order number (e.g., SO001)
• %partner_id% = Customer name
• %state% = Order status (draft, sale, done, etc.)
• %amount_total% = Total order amount
• %date_order% = Order date
• %user_id% = Salesperson name
• %commitment_date% = Delivery date
• %mobile% = Customer mobile number
• %email% = Customer email

Usage: Type %variable_name% in your template text'''
    )

    def _check_permissions(self):
        """Check if current user has permission to use SMS gateway."""
        self._cr.execute(
            'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s LIMIT 1',
            (self.env.uid,)
        )
        return bool(self._cr.fetchone())

    def _check_history_permissions(self):
        """Check if current user has permission to view SMS history.
        All users with any SMS gateway access can view shared history."""
        # Check if user has access to any SMS gateway
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

        # Ensure comprehensive access and visibility
        try:
            gateway._ensure_all_users_have_access()
        except Exception as e:
            _logger.warning(f"Could not ensure comprehensive access: {e}")

        # Check permissions
        if not self._check_permissions():
            raise UserError(_('You do not have permission to use gateway: %s') % gateway.name)

        _logger.info("Sending SMS via %s to %s", gateway.name, data.mobile_to)

        try:
            if gateway.method == 'http':
                result = self._send_http_sms(data, gateway)
            elif gateway.method == 'smpp':
                result = self._send_smpp_sms(data, gateway)
            else:
                raise UserError(_('Unsupported SMS method: %s') % gateway.method)

            # Create queue entry for tracking
            queue_vals = self._prepare_tunisiesms_queue(data, gateway.url)
            self.env['sms.tunisiesms.queue'].create(queue_vals)

            _logger.info("SMS sent successfully to %s", data.mobile_to)

        except Exception as e:
            _logger.error("SMS send failed: %s", str(e))
            # Log failure in history
            self._create_history_entry(
                gateway, data, '', 'error', data.mobile_to, str(e)
            )
            raise UserError(_('Failed to send SMS: %s') % str(e))

        return True

    def _check_queue(self):
        """Process SMS queue and send pending messages."""
        # AUTOMATIC FIX: Ensure all users have SMS access before processing queue
        try:
            _logger.info("🔧 Auto-triggering SMS visibility fix before processing queue")
            self._ensure_all_users_have_access()
        except Exception as fix_error:
            _logger.error(f"Queue SMS visibility fix failed: {fix_error}")
            # Continue anyway to attempt queue processing

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

            return message_id

        except Exception as e:
            _logger.error("HTTP SMS send failed: %s", str(e))
            # Create history entry for failure
            self._create_history_entry(
                gateway, data, '', 'error', data.mobile_to, str(e)
            )
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
                str(gateway.nostop or 0)
            )

            _logger.info(f"SOAP SMS sent successfully: {result}")

            # Create history entry
            self._create_history_entry(
                gateway, data, str(result), '200', data.mobile_to, 'SMPP SMS sent successfully'
            )

            return result

        except Exception as e:
            _logger.error(f"Error sending SMS via SOAP: {e}")
            # Create history entry for failure
            self._create_history_entry(
                gateway, data, '', 'error', data.mobile_to, str(e)
            )
            raise

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

    @api.model
    def create(self, vals):
        """Override create to automatically grant access to all users."""
        record = super().create(vals)
        
        # Only run access fix if we're not in a skip context
        if not self.env.context.get('skip_access_refresh'):
            try:
                record.with_context(skip_access_refresh=True)._ensure_all_users_have_access()
            except Exception as e:
                _logger.warning(f"Failed to ensure user access after create: {e}")
        
        return record

    def write(self, vals):
        """Override write to refresh user access when needed."""
        result = super().write(vals)

        # Only refresh user access if users_id field was modified and we're not in a refresh cycle
        if 'users_id' in vals and not self.env.context.get('skip_access_refresh'):
            try:
                # Use context to prevent recursion
                self.with_context(skip_access_refresh=True)._ensure_all_users_have_access()
            except Exception as e:
                _logger.warning(f"Failed to refresh user access after write: {e}")

        return result

    def _should_refresh_access(self):
        """Check if we should refresh user access (e.g., new users created)."""
        # Get all active users
        all_users = self.env['res.users'].search([('active', '=', True)])
        current_users = self.users_id

        # If there are users not in the gateway, we should refresh
        return len(all_users) != len(current_users)

    def _ensure_all_users_have_access(self):
        """Comprehensive SMS access fix - automatically runs fix_visibility.py logic."""
        try:
            # Prevent recursion by checking context
            if self.env.context.get('skip_access_refresh'):
                return
                
            _logger.info("🔧 Running automatic SMS visibility fix")
            
            # Get all active users
            all_users = self.env['res.users'].search([('active', '=', True)])
            current_users = self.users_id
            
            _logger.info(f"📊 Current users with SMS access: {len(current_users)}")
            _logger.info(f"👥 Total active users: {len(all_users)}")
            
            # Apply fix_visibility.py logic: Add all users to gateway permissions
            _logger.info("🔄 Adding all users to SMS gateway permissions...")
            
            # Use context to prevent recursion and directly call super().write()
            super(TunisieSMS, self.with_context(skip_access_refresh=True)).write({
                'users_id': [(6, 0, all_users.ids)]
            })
            
            # Verify the update
            updated_users = self.users_id
            _logger.info(f"✅ Updated users with SMS access: {len(updated_users)}")
            
            # Test SMS history visibility for each user
            _logger.info("🧪 Testing SMS history visibility for each user...")
            for user in all_users:
                try:
                    history_count = self.env['sms.tunisiesms.history'].sudo(user).search_count([])
                    _logger.debug(f"   {user.name}: {history_count} SMS history entries visible")
                except Exception as e:
                    _logger.warning(f"   {user.name}: Error - {e}")
            
            # Force cache refresh
            self.env.cache.invalidate()
            self.env.registry.clear_caches()
            
            # Don't commit during module installation, let Odoo handle it
            if not self.env.context.get('module_installation'):
                self.env.cr.commit()
                _logger.info("💾 SMS visibility fix committed to database")
            else:
                _logger.info("💾 SMS visibility fix applied (commit skipped during installation)")
            
        except Exception as e:
            _logger.error(f"Error in automatic SMS visibility fix: {e}")
            raise

    @api.model
    def refresh_user_access(self):
        """Public method to refresh user access - can be called from cron or manually."""
        gateways = self.search([])
        for gateway in gateways:
            gateway._ensure_all_users_have_access()

        # Force complete cache invalidation
        self.env.cache.invalidate()
        self.env.registry.clear_caches()

        # Commit changes
        self.env.cr.commit()

        return True

    def action_refresh_user_access(self):
        """Action to manually refresh user access from the UI."""
        try:
            self.refresh_user_access()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('SMS Access Refreshed'),
                    'message': _('SMS access has been refreshed for all users. Please refresh your browser to see the changes.'),
                    'type': 'success',
                    'sticky': True,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Refresh Failed'),
                    'message': _('Failed to refresh SMS access: %s') % str(e),
                    'type': 'danger',
                }
            }

    def create_test_sms_records(self):
        """Create test SMS records for debugging purposes."""
        try:
            # Create a few test SMS history records
            history_obj = self.env['sms.tunisiesms.history']

            test_records = [
                {
                    'name': 'Test SMS #1',
                    'gateway_id': self.id,
                    'sms': 'This is a test SMS message #1',
                    'to': '+216123456789',
                    'message_id': 'test_001',
                    'status_code': '200',
                    'status_mobile': '+216123456789',
                    'status_msg': 'Message sent successfully',
                    'date_create': fields.Datetime.now(),
                    'user_id': self.env.uid
                },
                {
                    'name': 'Test SMS #2',
                    'gateway_id': self.id,
                    'sms': 'This is a test SMS message #2',
                    'to': '+216987654321',
                    'message_id': 'test_002',
                    'status_code': '200',
                    'status_mobile': '+216987654321',
                    'status_msg': 'Message sent successfully',
                    'date_create': fields.Datetime.now(),
                    'user_id': self.env.uid
                },
                {
                    'name': 'Test SMS #3',
                    'gateway_id': self.id,
                    'sms': 'This is a test SMS message #3',
                    'to': '+216111222333',
                    'message_id': 'test_003',
                    'status_code': '200',
                    'status_mobile': '+216111222333',
                    'status_msg': 'Message sent successfully',
                    'date_create': fields.Datetime.now(),
                    'user_id': self.env.uid
                }
            ]

            created_records = []
            for record_data in test_records:
                record = history_obj.create(record_data)
                created_records.append(record)

            # Ensure current user has access
            self._ensure_all_users_have_access()
            
            # Clear caches (Odoo 14 compatible)
            self.env.cache.invalidate()
            self.env.registry.clear_caches()
            self.env.cr.commit()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Test SMS Records Created'),
                    'message': _('Created %d test SMS records. Please refresh your browser to see them.') % len(created_records),
                    'type': 'success',
                    'sticky': True,
                }
            }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error Creating Test Records'),
                    'message': _('Failed to create test SMS records: %s') % str(e),
                    'type': 'danger',
                }
            }

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

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        """Override search to implement shared queue access for authorized users."""
        # Check if current user has SMS gateway access
        if not self._check_user_sms_access():
            # If user has no SMS access, trigger refresh and check again
            self._trigger_access_refresh()
            if not self._check_user_sms_access():
                # Still no access, return empty recordset
                return super().search([('id', '=', False)], offset, limit, order, count)
        
        # User has SMS access - they can see all queue records
        return super().search(domain, offset, limit, order, count)
    
    def _check_user_sms_access(self):
        """Check if current user has access to SMS functionality."""
        self._cr.execute(
            'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s LIMIT 1',
            (self.env.uid,)
        )
        return bool(self._cr.fetchone())

    def _trigger_access_refresh(self):
        """Trigger comprehensive access refresh for the current user."""
        try:
            # Get the main SMS gateway
            gateway = self.env['sms.tunisiesms'].search([], limit=1)
            if gateway:
                _logger.info("Triggering comprehensive SMS access refresh for queue")
                gateway._ensure_all_users_have_access()
                
                # Additional immediate fix - ensure current user has access
                current_user = self.env.user
                if current_user not in gateway.users_id:
                    _logger.info(f"Adding current user {current_user.name} to SMS gateway")
                    gateway.write({
                        'users_id': [(4, current_user.id)]
                    })
                    
                # Force cache refresh
                self.env.cache.invalidate()
                self.env.registry.clear_caches()
                
        except Exception as e:
            _logger.error(f"Error triggering access refresh: {e}")


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

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        """Override search to implement shared history access for authorized users."""
        # Check if current user has SMS gateway access
        if not self._check_user_sms_access():
            # If user has no SMS access, trigger refresh and check again
            self._trigger_access_refresh()
            if not self._check_user_sms_access():
                # Still no access, return empty recordset
                return super().search([('id', '=', False)], offset, limit, order, count)
        
        # User has SMS access - they can see all history records
        return super().search(domain, offset, limit, order, count)
    
    def _check_user_sms_access(self):
        """Check if current user has access to SMS functionality."""
        self._cr.execute(
            'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s LIMIT 1',
            (self.env.uid,)
        )
        return bool(self._cr.fetchone())

    def _trigger_access_refresh(self):
        """Trigger comprehensive access refresh for the current user."""
        try:
            # Get the main SMS gateway
            gateway = self.env['sms.tunisiesms'].search([], limit=1)
            if gateway:
                _logger.info("Triggering comprehensive SMS access refresh for history")
                gateway._ensure_all_users_have_access()
                
                # Additional immediate fix - ensure current user has access
                current_user = self.env.user
                if current_user not in gateway.users_id:
                    _logger.info(f"Adding current user {current_user.name} to SMS gateway")
                    gateway.write({
                        'users_id': [(4, current_user.id)]
                    })
                    
                # Force cache refresh
                self.env.cache.invalidate()
                self.env.registry.clear_caches()
                
        except Exception as e:
            _logger.error(f"Error triggering access refresh: {e}")

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

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to automatically send SMS for new orders."""
        orders = super(SaleOrderSMS, self).create(vals_list)

        # Process SMS for new orders
        for order in orders:
            try:
                self._send_automatic_sms(order, is_new_order=True)
            except Exception as e:
                _logger.error("Failed to send automatic SMS for new order %s: %s", order.name, str(e))

        return orders

    def write(self, vals):
        """Override write to automatically send SMS when order status changes."""
        # Store old states before update
        old_states = {order.id: order.state for order in self}

        # Call parent write method
        result = super(SaleOrderSMS, self).write(vals)

        # Check if state changed and send SMS if needed
        if 'state' in vals:
            for order in self:
                old_state = old_states.get(order.id)
                if old_state != order.state:
                    try:
                        self._send_automatic_sms(order, is_new_order=False, old_state=old_state)
                    except Exception as e:
                        _logger.error("Failed to send automatic SMS for order state change %s: %s", order.name, str(e))

        return result

    def _send_automatic_sms(self, order, is_new_order=False, old_state=None):
        """Send automatic SMS for order creation or status change."""
        # Get SMS gateway
        sms_gateway = self.env['sms.tunisiesms'].search([('id', '=', 1)], limit=1)
        if not sms_gateway:
            _logger.warning("No SMS gateway configured for automatic SMS")
            return

        # AUTOMATIC FIX: Ensure all users have SMS access before sending
        try:
            _logger.info("🔧 Auto-triggering SMS visibility fix before sending SMS")
            sms_gateway._ensure_all_users_have_access()
        except Exception as fix_error:
            _logger.error(f"Auto SMS visibility fix failed: {fix_error}")
            # Continue anyway to attempt SMS send

        # Check if automatic SMS is enabled globally
        if not sms_gateway.auto_sms_enabled:
            _logger.info("Automatic SMS disabled globally, skipping SMS for order %s", order.name)
            return

        # Check specific automatic SMS settings
        if is_new_order and not sms_gateway.auto_sms_on_create:
            _logger.info("Automatic SMS on order creation disabled, skipping SMS for order %s", order.name)
            return

        if not is_new_order and not sms_gateway.auto_sms_on_status_change:
            _logger.info("Automatic SMS on status change disabled, skipping SMS for order %s", order.name)
            return

        # Check if partner has mobile number
        partner_mobile = order.partner_id.mobile
        if not partner_mobile:
            _logger.info("No mobile number for partner %s, skipping SMS", order.partner_id.name)
            return

        # Get SMS template and permission based on current order state
        sms_template, send_permission = self._get_order_sms_config(order.state, sms_gateway)

        if not send_permission:
            _logger.info("SMS disabled for order state '%s', skipping SMS for order %s", order.state, order.name)
            return

        if not sms_template:
            _logger.info("No SMS template configured for order state '%s', skipping SMS for order %s", order.state, order.name)
            return

        # Replace template variables
        final_message = self._replace_order_variables(sms_template, order)

        if not final_message.strip():
            _logger.warning("Empty SMS message after template processing for order %s", order.name)
            return

        # Create SMS data
        sms_data = self.env['partner.tunisiesms.send'].create({
            'gateway': sms_gateway.id,
            'mobile_to': partner_mobile,
            'text': final_message
        })

        # Send SMS
        try:
            self.env['sms.tunisiesms'].send_msg(sms_data)

            # Log successful SMS
            action_type = "New Order" if is_new_order else f"State Change ({old_state} → {order.state})"
            _logger.info("Automatic SMS sent for %s: Order %s to %s", action_type, order.name, partner_mobile)

            # Update SMS status tracking
            current_time = fields.Datetime.now()
            order.write({
                'tunisie_sms_status': 1,  # Sent
                'tunisie_sms_send_date': current_time,
                'tunisie_sms_write_date': current_time,
                'tunisie_sms_msisdn': partner_mobile,
            })

        except Exception as e:
            _logger.error("Failed to send automatic SMS for order %s: %s", order.name, str(e))
            # Update SMS status to error
            current_time = fields.Datetime.now()
            order.write({
                'tunisie_sms_status': 3,  # Error
                'tunisie_sms_send_date': current_time,
                'tunisie_sms_write_date': current_time,
                'tunisie_sms_msisdn': partner_mobile,
            })

    def action_send_sms_now(self):
        """Manual action to send SMS for current order state."""
        for order in self:
            try:
                self._send_automatic_sms(order, is_new_order=False, old_state=None)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('SMS Sent'),
                        'message': _('SMS sent successfully for order %s') % order.name,
                        'type': 'success',
                    }
                }
            except Exception as e:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('SMS Error'),
                        'message': _('Failed to send SMS for order %s: %s') % (order.name, str(e)),
                        'type': 'danger',
                    }
                }


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

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to automatically send SMS for new partners."""
        partners = super(ResPartnerSMS, self).create(vals_list)

        # Process SMS for new partners (only for customers, not vendors or companies)
        for partner in partners:
            if partner.is_company or partner.supplier_rank > 0:
                continue  # Skip companies and vendors
            try:
                self._send_automatic_partner_sms(partner)
            except Exception as e:
                _logger.error("Failed to send automatic SMS for new partner %s: %s", partner.name, str(e))

        return partners

    def _send_automatic_partner_sms(self, partner):
        """Send automatic SMS notification for new partner creation."""
        # Get SMS gateway
        sms_gateway = self.env['sms.tunisiesms'].search([('id', '=', 1)], limit=1)
        if not sms_gateway:
            _logger.warning("No SMS gateway configured for automatic partner SMS")
            return

        # Check if automatic SMS is enabled globally and for partner creation
        if not sms_gateway.auto_sms_enabled or not sms_gateway.status_res_partner_create:
            _logger.info("Automatic partner SMS disabled, skipping SMS for partner %s", partner.name)
            return

        # Get SMS template
        sms_template = sms_gateway.res_partner_sms_create
        if not sms_template:
            _logger.info("No SMS template configured for partner creation, skipping SMS for partner %s", partner.name)
            return

        # Get administrator mobile for notifications
        admin_partner = self.search([('name', '=', 'Administrator')], limit=1)
        admin_mobile = admin_partner.mobile if admin_partner else None

        if not admin_mobile:
            _logger.warning("Administrator mobile not configured, cannot send partner creation SMS")
            return

        # Replace template variables
        final_message = self.env['sms.tunisiesms.generic'].replace_with_table_attribute(
            sms_template, 'res_partner', partner
        )

        if not final_message.strip():
            _logger.warning("Empty SMS message after template processing for partner %s", partner.name)
            return

        # Create SMS data
        sms_data = self.env['partner.tunisiesms.send'].create({
            'gateway': sms_gateway.id,
            'mobile_to': admin_mobile,
            'text': final_message
        })

        # Send SMS
        try:
            self.env['sms.tunisiesms'].send_msg(sms_data)

            # Log successful SMS
            _logger.info("Automatic SMS sent for new partner: %s to admin %s", partner.name, admin_mobile)

            # Update SMS status tracking
            current_time = fields.Datetime.now()
            partner.write({
                'tunisie_sms_status': 1,  # Sent
                'tunisie_sms_send_date': current_time,
                'tunisie_sms_write_date': current_time,
            })

        except Exception as e:
            _logger.error("Failed to send automatic SMS for partner %s: %s", partner.name, str(e))
            # Update SMS status to error
            current_time = fields.Datetime.now()
            partner.write({
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
                    if field_value is None:
                        replacement = ''
                    elif field_value is False:
                        replacement = 'No'  # Convert False to human-readable string
                    elif field_value is True:
                        replacement = 'Yes'  # Convert True to human-readable string
                    elif hasattr(field_value, 'name'):
                        # Handle Many2one fields
                        replacement = field_value.name
                    elif isinstance(field_value, (list, tuple)):
                        # Handle One2many/Many2many fields
                        replacement = ', '.join(str(item) for item in field_value)
                    else:
                        replacement = str(field_value)

                    # Ensure replacement is always a string
                    if not isinstance(replacement, str):
                        replacement = str(replacement)

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
            # Create with skip_access_refresh to prevent recursion during module installation
            gateway_obj.with_context(skip_access_refresh=True, module_installation=True).create({
                'name': 'TUNISIESMS'
            })

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
                str(sms.tag or ''),
                str(sms.nostop or 0)
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

    @api.model
    def create(self, vals):
        """Override create to automatically grant SMS access to new users."""
        user = super().create(vals)

        # Grant SMS access to newly created active users
        if user.active:
            try:
                # Find all SMS gateways and grant access
                gateways = self.env['sms.tunisiesms'].search([])
                for gateway in gateways:
                    gateway._ensure_all_users_have_access()
                _logger.info(f"Granted SMS access to new user: {user.name}")
            except Exception as e:
                _logger.error(f"Error granting SMS access to new user {user.name}: {e}")

        return user

    def write(self, vals):
        """Override write to refresh SMS access when user is activated."""
        result = super().write(vals)

        # If user was activated, ensure they have SMS access
        if 'active' in vals and vals['active']:
            try:
                gateways = self.env['sms.tunisiesms'].search([])
                for gateway in gateways:
                    gateway._ensure_all_users_have_access()
                _logger.info(f"Refreshed SMS access for activated users")
            except Exception as e:
                _logger.error(f"Error refreshing SMS access for activated users: {e}")

        return result
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: