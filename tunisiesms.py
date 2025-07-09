import time
from typing import Match
import urllib
import urllib.parse
from odoo import api, fields, models, _
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import json
import jxmlease
import requests

import logging
_logger = logging.getLogger(__name__)
try:
    from SOAPpy import WSDL
except :
    _logger.warning("ERROR IMPORTING SOAPpy, if not installed, please install it:"
    " e.g.: apt-get install python-soappy")


class TUNISIESMS(models.Model):

    _name = 'sms.tunisiesms'
    _description = 'TUNISIE SMS'

    name = fields.Char('Gateway Name', default='TUNISIESMS' ,readonly=True, required=True)
    url = fields.Char('Gateway URL', 
            required=True , readonly=True, default='https://api.l2t.io/tn/v0/api/api.aspx' ,help='Base url for message')
    property_ids = fields.One2many('sms.tunisiesms.parms',
            'gateway_id', 'Parameters')
    history_line = fields.One2many('sms.tunisiesms.history',
            'gateway_id', 'History')
    method = fields.Selection([
                ('http', 'HTTP Method'),
                ('smpp', 'SMPP Method')
            ], 'API Method', readonly=True,  default = 'http')
    state = fields.Selection([
                ('new', 'Not Verified'),
                ('waiting', 'Waiting for Verification'),
                ('confirm', 'Verified'),
            ], 'Gateway Status',  default= 'new', readonly=True)
    users_id = fields.Many2many('res.users',
            'res_smsserver_group_rel', 'sid', 'uid', 'Users Allowed')
    code = fields.Char('Verification Code', )
    body = fields.Text('Message',
            help="The message text that will be send along with the email which is send through this server")
    validity = fields.Integer('Validity',
            help='The maximum time -in minute(s)- before the message is dropped', default = 10)
    classes = fields.Selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit')
            ], 'Class',
            help='The SMS class: flash(0),phone display(1),SIM(2),toolkit(3)', default ='1')
    deferred = fields.Integer('Deferred',
            help='The time -in minute(s)- to wait before sending the message', default = 0)
    priority = fields.Selection([
                ('0', '0'),
                ('1', '1'),
                ('2', '2'),
                ('3', '3')
            ], 'Priority', help='The priority of the message ')
    coding = fields.Selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ],'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode')

    tag = fields.Char('Tag',  help='an optional tag')
    nostop = fields.Boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message', default = True )
    char_limit = fields.Boolean('Character Limit' , default = True)

    order_draft_sms = fields.Text('Order SMS Draft')
    status_order_draft = fields.Boolean('Status Order Draft', default=True)

    order_sent_sms = fields.Text('Order SMS Sent')
    status_order_sent = fields.Boolean('Status Order Sent', default=True)

    order_waiting_sms = fields.Text('Order SMS Waiting')
    status_order_waiting = fields.Boolean('Status Order Waiting', default=True)

    order_sale_sms = fields.Text('Order SMS Sale')
    status_order_sale = fields.Boolean('Status Order Sale', default=True)

    order_done_sms = fields.Text('Order SMS Done')
    status_order_done = fields.Boolean('Status Order Done', default=True)

    order_cancel_sms = fields.Text('Order SMS Cancel')
    status_order_cancel = fields.Boolean('Status Order Cancel', default=True)

    res_partner_sms_create = fields.Text('New Contact Created SMS')
    status_res_partner_create = fields.Boolean('Status New Contact Created', default=True)

    mobile_url_params = fields.Char('mobile_url_params', default='mobile')
    sms_url_params = fields.Char('sms_url_params', default='sms')
    fct_url_params = fields.Char('fct_url_params', default='fct')
    sender_url_params = fields.Char('sender_url_params')
    key_url_params = fields.Text('key_url_params')

    code_error_status = fields.One2many('sms.tunisiesms.code.error', 
            'gateway_id', 'Code Errors', readonly=True)

    label_order = fields.Char( 
            required=True , readonly=True, default='Merci de mentionner ces champs au niveau de votre texte : %STATE%  %DATE%  %NAME%')

    def _check_permissions(self):
        self._cr.execute('select * from res_smsserver_group_rel where  uid=%s' % ( self.env.uid))
        data = self._cr.fetchall()
        if len(data) <= 0:
            return False
        return True


    def _prepare_tunisiesms_queue(self, data, name):
        return {
            'name': name,
            'gateway_id': data.gateway.id,
            'state': 'draft',
            'mobile': data.mobile_to,
            'msg': data.text,
            'validity': data.validity, 
            'classes': data.classes1, 
            'coding': data.coding,
            'nostop': data.nostop1,
        }

    def send_msg(self, data):
        if self._context is None:
            self._context = {}
        gateway = data.gateway
        print(f"Data from send message  : {data}")
        if gateway:
            if not self._check_permissions():

                raise UserError(_('You have no permission to access %s') % (gateway.name,) )
            url = gateway.url
            name = url
            if gateway.method == 'http':
                prms = {}
                prms['mobile'] = data.mobile_to
                prms['sms'] = data.text
                prms['fct'] ='sms'
                prms['sender'] = gateway.sender_url_params
                prms['key'] = gateway.key_url_params

                params = urllib.parse.urlencode(prms)
                name = url + "?" + params

            queue_obj = self.env['sms.tunisiesms.queue']
            vals = self._prepare_tunisiesms_queue(data, name )
            queue_obj.create(vals)
        return True

        
    def _check_queue(self):
        if self._context is None:
            self._context = {}
        queue_obj = self.env['sms.tunisiesms.queue']
        history_obj = self.env['sms.tunisiesms.history']
        sids = queue_obj.search( [
                ('state', '!=', 'send'),
                ('state', '!=', 'sending')
            ], limit=30)
        sids.write({'state': 'sending'})
        error_ids = []
        sent_ids = []
        
        
        for sms in sids:
            if sms.gateway_id.char_limit:
                if len(sms.msg) > 160:
                    error_ids.append(sms.id)
                    continue
            if sms.gateway_id.method == 'http':
                try:
                    print("URL ===>")
                    print(sms.name)
                    print("*************** response ***************")
                    response = urllib.request.urlopen(sms.name).read()
                    print(response)
                    print("*********************")
                    root = jxmlease.parse(response)
                    print(root)
                    message_id = root['response']['status']['message_id'].get_cdata()
                    status_code = root['response']['status']['status_code'].get_cdata()
                    status_mobile = root['response']['status']['status_mobile'].get_cdata()
                    status_msg = root['response']['status']['status_msg'].get_cdata()
                except Exception:
                    
                    
                    raise UserError(_('Error %s') % (e) )                    
            if sms.gateway_id.method == 'smpp':
                for p in sms.gateway_id.property_ids:
                    if p.type == 'user':
                        login = p.value
                    elif p.type == 'password':
                        pwd = p.value
                    elif p.type == 'sender':
                        sender = p.value
                    elif p.type == 'sms':
                        account = p.value
                try:
                    soap = WSDL.Proxy(sms.gateway_id.url)
                    message = ''
                    if sms.coding == '2':
                        message = str(sms.msg).decode('iso-8859-1').encode('utf8')
                    if sms.coding == '1':
                        message = str(sms.msg)
                    result = soap.telephonySmsUserSend(str(login), str(pwd),
                        str(account), str(sender), str(sms.mobile), message,
                        int(sms.validity), int(sms.classes), int(sms.deferred),
                        int(sms.priority), int(sms.coding),str(sms.gateway_id.tag), int(sms.gateway_id.nostop))
                except Exception:
                    raise UserError(_('Error %s') % (e) )    
                
            history_obj.create( {
                            'name': _('SMS Sent'),
                            'gateway_id': sms.gateway_id.id,
                            'sms': sms.msg,
                            'to': sms.mobile,
                            'message_id' :message_id,
                            'status_code': status_code,
                            'status_mobile': status_mobile,
                            'status_msg': status_msg,
                            'date_create': datetime.now()
                        })
            sent_ids.append(sms.id)
        for sent_id in sent_ids:
            browse_record = queue_obj.browse(sent_id)
            browse_record.state = 'send'
        for id in  error_ids:
          browse_record = queue_obj.browse(sent_id)     
          browse_record.state = 'error'
          browse_record.error =  'Size of SMS should not be more then 160 char'
        return True

   
    
    @api.model
    def alternative_action_get_tunisiesms(self):
        
        context = self.env.context
        tunisiesms = self.sudo().search([["id", "=", (1)]], limit=1)
        
        res_id = self.env.uid
        action = {
            "type" : "ir.actions.act_window",
            'context': context,
            "res_model" : "sms.tunisiesms",
            'view_type': 'form',
            "view_mode": "form",
            "view_id": self.env.ref("sms_tunisiesms_form").id,
            "res_id": tunisiesms.id if tunisiesms.id else False,
            'target': 'inline',
        }
        return action

    def update_sms_client(self):
        if self._context is None:
            self._context = {}
        
        for data in self:
            print(f"sms_client : {data}")
            gateway_obj = self.env['sms.tunisiesms']
            gateway_obj.update(data)
            return True

class SMSQueue(models.Model):

    _name = 'sms.tunisiesms.queue'
    
    _description = 'SMS Queue'


    name =  fields.Text('SMS Request', 
            required=True, readonly=True,
            states={'draft': [('readonly', False)]})
    msg = fields.Text('SMS Text', 
            required=True, readonly=True,
            states={'draft': [('readonly', False)]})
    mobile = fields.Char('Mobile No', 
            required=True, readonly=True,
            states={'draft': [('readonly', False)]})
    gateway_id=  fields.Many2one('sms.tunisiesms',
            'SMS Gateway', readonly=True,
            states={'draft': [('readonly', False)]})
    state = fields.Selection([
            ('draft', 'Queued'),
            ('sending', 'Waiting'),
            ('send', 'Sent'),
            ('error', 'Error'),
        ], 'Message Status', readonly=True,  default  =  'draft')
    error = fields.Text('Last Error', 
            readonly=True,
            states={'draft': [('readonly', False)]})
    date_create = fields.Datetime('Date', readonly=True,  default=lambda self: fields.Datetime.now())
    validity = fields.Integer('Validity',
            help='The maximum time -in minute(s)- before the message is dropped')
    priority= fields.Selection([
                ('0', '0'),
                ('1', '1'),
                ('2', '2'),
                ('3', '3')
            ], 'Priority', help='The priority of the message ')

    classes  = fields.Selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit')
            ], 'Class', help='The sms class: flash(0), phone display(1), SIM(2), toolkit(3)')
    deferred = fields.Integer('Deferred',
            help='The time -in minute(s)- to wait before sending the message', default = 0)
    coding = fields.Selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ], 'Coding', help='The sms coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char('Tag',
            help='An optional tag')
    nostop=  fields.Boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message')
        
  
class Properties(models.Model):

    _name = 'sms.tunisiesms.parms'
    _description = 'SMS Client Properties'

    name = fields.Char('Property name', 
             help='Name of the property whom appear on the URL')
    value = fields.Char('Property value', 
             help='Value associate on the property for the URL')
    gateway_id = fields.Many2one('sms.tunisiesms', 'SMS Gateway')
    type = fields.Selection([
                ('user', 'User'),
                ('password', 'Password'),
                ('sender', 'Sender Name'),
                ('to', 'Recipient No'),
                ('sms', 'SMS Message'),
                ('extra', 'Extra Info')
            ], 'API Method',
            help='If parameter concern a value to substitute, indicate it')

class HistoryLine(models.Model):

    _name = 'sms.tunisiesms.history'
    _description = 'SMS Client History'


    name = fields.Char('Description',  required=True, readonly=True)
    date_create = fields.Datetime('Date', readonly=True,  default=lambda self: fields.Datetime.now())
    user_id = fields.Many2one('res.users', 'Username', readonly=True)
    gateway_id = fields.Many2one('sms.tunisiesms', 'SMS Gateway', ondelete='set null')
    to = fields.Char('Mobile No',  readonly=True)
    sms = fields.Text('SMS',  readonly=True)

    message_id =fields.Char('Message_ID')
    status_code =fields.Char('Status')
    status_mobile =fields.Char('Mobile')
    status_msg =fields.Char('Msg Status')
    dlr_msg = fields.Char('DLR')
 
    def get_dlr_status(self):

        history_obj = self.env['sms.tunisiesms.history']
        hids = history_obj.search( [('dlr_msg', '=', False)], order='date_create desc', limit=30)
        hids = hids.search( [('message_id', '!=', ('1'))], order='date_create desc', limit=30)
        print(f"history ids   : {hids}")
        for obj_hist in hids:
            print("GETTING MSG ID VALUE")
            message_id = obj_hist.message_id
            print(f"message_id  : {message_id}")

            url = obj_hist.gateway_id.url
            prms = {}
            prms['fct'] = 'dlr'
            prms['key'] = obj_hist.gateway_id.key_url_params
            prms['msg_id'] = message_id

            params = urllib.parse.urlencode(prms)
            name = url + "?" + params
            
            response = urllib.request.urlopen(name).read()
            root = jxmlease.parse(response)
            message_id_from_xml = root['acknowledgement']['message']['message_id'].get_cdata()
            
            acknowledgement = root['acknowledgement']['message']['acknowledgement'].get_cdata()
            
            acknowledgement_date = root['acknowledgement']['message']['acknowledgement_date'].get_cdata()

            obj_hist.write({'dlr_msg': acknowledgement})  

class partner_sms_send(models.Model):

    _name = "partner.tunisiesms.send"
    _description = 'Partner SMS Send'


    @api.model
    def _default_get_mobile(self):
        if self._context is None:
            self._context = {}
        partner_pool = self.env['res.partner']
        active_ids = self._context.get('active_ids')
        res = {}
        i = 0
        for partner in partner_pool.browse(active_ids): 
            i += 1           
            res = partner.mobile
        if i > 1:
            raise UserError(_('You can only select one partner'))
        return res

    @api.model
    def _default_get_gateway(self):
        if self._context is None:
            self._context = {}
        sms_obj = self.env['sms.tunisiesms']
        gateway_ids = sms_obj.search([], limit=1)
        return gateway_ids and gateway_ids[0] or False



    @api.onchange('gateway_id')
    def onchange_gateway(self):
        if self._context is None:
            context = {}
        sms_obj = self.env['sms.tunisiesms']
        if not gateway_id:
            return {}
        gateway = sms_obj.browse( gateway_id, context=context)
        return {
            'value': {
                'validity': gateway.validity, 
                'classes': gateway.classes,
                'deferred': gateway.deferred,
                'priority': gateway.priority,
                'coding': gateway.coding,
                'tag': gateway.tag,
                'nostop': gateway.nostop,
            }
        }

  
    mobile_to = fields.Char('To', required=True, default = _default_get_mobile)

    app_id = fields.Char('API ID' )

    user = fields.Char('Login' )

    password = fields.Char('Password')

    text = fields.Text('SMS Message', required=True)

    gateway = fields.Many2one('sms.tunisiesms', 'SMS Gateway', default = _default_get_gateway)

    validity = fields.Integer('Validity',
            help='the maximum time -in minute(s)- before the message is dropped')

    classes1 = fields.Selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit')
            ], 'Class', help='the sms class: flash(0), phone display(1), SIM(2), toolkit(3)')

    deferred = fields.Integer('Deferred',
            help='the time -in minute(s)- to wait before sending the message', default = 0)

    priority = fields.Selection([
                ('0','0'),
                ('1','1'),
                ('2','2'),
                ('3','3')
            ], 'Priority', help='The priority of the message')

    coding = fields.Selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ], 'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode')


    nostop1 = fields.Boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message')
    

    def sms_send(self):
        if self._context is None:
            self._context = {}
        client_obj = self.env['sms.tunisiesms']
        for data in self:
            if not data.gateway:
                raise UserError(_('You can only select one partner'))
            else:
                client_obj.send_msg(data)
        return True
     
class OrderSaleSms(models.Model):
     _inherit = 'sale.order'

     tunisie_sms_status = fields.Integer(default =0)
     tunisie_sms_send_date = fields.Char('tunisie_sms_send_date')
     tunisie_sms_write_date = fields.Char('tunisie_sms_write_date')
     tunisie_sms_msisdn = fields.Char('tunisie_sms_msisdn')

     def GetStateOrderToSend(self):
        date_now = datetime.now()
      
        status_order = self.env['sale.order']
        sms_client = self.env['sms.tunisiesms']
        order_list = status_order.search([('tunisie_sms_status','=',(0))])
        
        order_sms_text = sms_client.search([('id','=',(1))])
        
      
        for order in order_list:
            mobile_to= order.partner_id.mobile
            if mobile_to:
                
                
                data = self.env['partner.tunisiesms.send']
                
                name_order = order.name
               
                date_order = order.write_date
                state_order= order.state

                #print(f"state_order   : {state_order}")

                send_permission = False
                if state_order == 'draft':
                   text_to_send = order_sms_text.order_draft_sms
                   send_permission = order_sms_text.status_order_draft

                if state_order == 'sent':
                   text_to_send = order_sms_text.order_sent_sms
                   send_permission = order_sms_text.status_order_sent
                
                if state_order == 'waiting':
                   text_to_send = order_sms_text.order_waiting_sms
                   send_permission = order_sms_text.status_order_waiting

                if state_order == 'sale':
                   text_to_send = order_sms_text.order_sale_sms
                   send_permission = order_sms_text.status_order_sale

                if state_order == 'done':
                   text_to_send = order_sms_text.order_done_sms
                   send_permission = order_sms_text.status_order_done

                if state_order == 'cancel':
                   text_to_send = order_sms_text.order_cancel_sms
                   send_permission = order_sms_text.status_order_cancel
                
               
                text_to_send = self.replace_with_table_attribute(text_to_send,'sale_order',order)
                print(f"text_to_send  : {text_to_send}")
             
                values = {'gateway': order_sms_text.id, 'mobile_to': mobile_to, 'text': text_to_send }
                new_partner_sms = data.create(values)
               
                print(f"Data gateway id  : {new_partner_sms.gateway.id}")

                #if order_sms_text.status_order == True:
                if send_permission == True:
                   sms_client.send_msg(new_partner_sms)
                   order.tunisie_sms_status = 1
                   order.tunisie_sms_send_date = date_now
                   order.tunisie_sms_write_date = date_now
                   order.tunisie_sms_msisdn =mobile_to
                else:
                    # when status_order in sms_tunisiesms == false
                   order.tunisie_sms_status = 3
                   order.tunisie_sms_send_date = date_now
                   order.tunisie_sms_write_date = date_now
                   order.tunisie_sms_msisdn =mobile_to
                #UPDATE
            else:
                print("MSISDN DOES NOT EXIST ==>")
                order.tunisie_sms_status = 2
                order.tunisie_sms_send_date = date_now
                order.tunisie_sms_write_date = date_now

     def replace_with_table_attribute(self,text_to_change,table_name,object):

       
        query = """ SELECT column_name FROM information_schema.columns WHERE table_name = '%table_name%' """
        query = query.replace('%table_name%', table_name)
        self._cr.execute(query)
        data = self._cr.fetchall()
        

        for column in data:
            p = "%"
            column_to_change = p + column[0] + p
            text_to_change = text_to_change.replace(column_to_change, str(object[column[0]]))
        
        return text_to_change


class ResPartnerSms(models.Model):
    _inherit = 'res.partner'

    tunisie_sms_status = fields.Integer(default=0)
    tunisie_sms_send_date = fields.Char('tunisie_sms_send_date')
    tunisie_sms_write_date = fields.Char('tunisie_sms_write_date')
    #tunisie_sms_msisdn = fields.Char('restunisie_sms_msisdn')


    def GetStateResPartnerToSend(self):
        date_now = datetime.now()

        res_partner = self.env['res.partner']
        tunisie_sms_obj = self.env['sms.tunisiesms']
        res_partner_list = res_partner.search([('tunisie_sms_status', '=', (0))])
        res_partner_administrator = res_partner.search([('name', '=', 'Administrator')])
        tunisie_sms = tunisie_sms_obj.search([('id', '=', (1))])

        for res_partner in res_partner_list:

            mobile_to = res_partner_administrator.mobile
            if mobile_to:
                print("MSISDN EXIST ===>")
                data = self.env['partner.tunisiesms.send']

                send_permission = False

                send_permission = tunisie_sms.status_res_partner_create
                text_to_send = tunisie_sms.res_partner_sms_create


                text_to_send = self.env['sms.tunisiesms.generic'].replace_with_table_attribute(text_to_send, 'res_partner', res_partner)

                values = {'gateway': tunisie_sms.id, 'mobile_to': mobile_to, 'text': text_to_send}
                new_partner_sms = data.create(values)

                if send_permission == True:
                    tunisie_sms_obj.send_msg(new_partner_sms)
                    res_partner.tunisie_sms_status = 1
                    res_partner.tunisie_sms_send_date = date_now
                    res_partner.tunisie_sms_write_date = date_now
                else:
                    res_partner.tunisie_sms_status = 3
                    res_partner.tunisie_sms_send_date = date_now
                    res_partner.tunisie_sms_write_date = date_now
                    
                # UPDATE
            else:
                print("MSISDN DOES NOT EXIST ==>")
                res_partner.tunisie_sms_status = 2
                res_partner.tunisie_sms_send_date = date_now
                res_partner.tunisie_sms_write_date = date_now

class SMSCodeStatus(models.Model):

    _name = 'sms.tunisiesms.code.error'
    _description = 'SMS Code Status'

    code = fields.Char('Code Status')
    libelle = fields.Char('Signification')
    gateway_id = fields.Many2one('sms.tunisiesms', 'SMS Gateway')


    @api.model
    def insert_in_table_code_errors(self):

        code_errors_list = [{"statut":"200", "message":"message test"},
                       {"statut":"400", "message":"message test 400"}]
        print(f"Code errors list  : {code_errors_list}")

        for data in code_errors_list:
            code_errors_obj = self.env['sms.tunisiesms.code.error']
            print(f"Code errors object  : {data}")

        return True

class TUNISIESMStGeneric(models.Model):

    _name = 'sms.tunisiesms.generic'
    _description = 'TUNISIE SMS Generic'

    def replace_with_table_attribute(self, text_to_change, table_name, object):
        query = """ SELECT column_name FROM information_schema.columns WHERE table_name = '%table_name%' """
        query = query.replace('%table_name%', table_name)
        self._cr.execute(query)
        data = self._cr.fetchall()

        p = "%"
        for column in data:
            column_to_change = p + column[0] + p
            text_to_change = text_to_change.replace(column_to_change, str(object[column[0]]))

        return text_to_change

class TUNISIESMStSetup(models.Model):

    _name = 'sms.tunisiesms.setup'
    _description = 'TUNISIE SMS Setup'
    
    @api.model
    def insert_in_table_code_errors(self):
        
        code_errors_obj = self.env['sms.tunisiesms.code.error']
        code_errors_list = [{"status":"200", "message":"![CDATA[OK]]"},
                            {"status":"400", "message":"absence d'id"},
                            {"status":"401", "message":"id non autorisé"},
                            {"status":"402", "message":"crédit insuffisant"},
                            {"status":"403", "message":"module non autorisé"},
                            {"status":"420", "message":"quota journalier dépassé"},
                            {"status":"430", "message":"contenu manquant"},
                            {"status":"431", "message":"destination manquante"},
                            {"status":"440", "message":"contenu trop long"},
                            {"status":"441", "message":"destination non autorisée"},
                            {"status":"442", "message":"sender non autorisée"},
                            {"status":"500", "message":"erreur interne"},
                            {"status":"501", "message":"date non valide"},
                            {"status":"502", "message":"heure non valide"}]

        code_errors_obj_list = code_errors_obj.search([])
        print("check changes")
        if len(code_errors_obj_list) > len(code_errors_list) or len(code_errors_obj_list) < len(code_errors_list):
           self._cr.execute('delete from sms_tunisiesms_code_error')
           print("length list")
           print(len(code_errors_obj_list))
           for data in code_errors_list:
               new_code_errors_obj = self.env['sms.tunisiesms.code.error']
               print("code status")
               print(data["status"])
               print(data["message"])
               new_code_error_obj = {'code': data["status"], 'libelle': data["message"],'gateway_id': 1}
               new_code_errors_obj.create(new_code_error_obj)

        print("no update")

        return True


    @api.model
    def update_table_order_sale_from_zero_to_4(self):
        status_order = self.env['sale.order']
        ord_ids_list_started = status_order.search([('tunisie_sms_status','=',(4))])
        
        if len(ord_ids_list_started) == 0:
            ord_ids = status_order.search([('tunisie_sms_status','=',(0))])
            for ord_id in ord_ids:
                ord_id.write({'tunisie_sms_status': 4}) 

        return True

    @api.model
    def update_table_res_partner_from_zero_to_4(self):
        res_partner_list = self.env['res.partner']
        ids_res_partner_list = res_partner_list.search([('tunisie_sms_status', '=', (4))])

        if len(ids_res_partner_list) == 0:
            partner_ids = res_partner_list.search([('tunisie_sms_status', '=', (0))])
            for partner_id in partner_ids:
                partner_id.write({'tunisie_sms_status': 4})

        return True

    @api.model
    def create_table_sms_tunisiesms_setup(self):
        tunisie_sms = self.env['sms.tunisiesms']

        tunisie_sms_list = tunisie_sms.search([])
        if len(tunisie_sms_list) == 0:
            tunisie_sms.create({'name': 'TUNISIESMS'}) 
    
        return True

    @api.model
    def create_trigger_sale_update_in_setup(self):
        tunisie_sms = self.env['sms.tunisiesms']

        tunisie_sms_list = tunisie_sms.search([])

        #if len(tunisie_sms_list) == 0:
        self._cr.execute( """CREATE OR REPLACE FUNCTION fct_sale_update()
                                    RETURNS trigger
                                    LANGUAGE 'plpgsql'
                                    COST 100
                                    VOLATILE NOT LEAKPROOF
                                AS $BODY$

                                BEGIN   
                                /*************UPDATE tunisie sms STATUS*************************/

                                NEW.tunisie_sms_status = 0;

                                RETURN NEW;

                                END;
                                $BODY$;
                                 """)
            
        self._cr.execute( """DROP TRIGGER IF EXISTS tr_sale_update
                                ON sale_order;
                                CREATE TRIGGER tr_sale_update
                                        BEFORE UPDATE
                                        ON sale_order
                                        FOR EACH ROW
                                        WHEN (NEW.state <> OLD.state)
                                        EXECUTE PROCEDURE fct_sale_update();""") 
    
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: