

{
    "name": "Tunisie SMS",
    "version": "14.0.0.0",
    "depends": ["base","mail","partner_autocomplete","sale"],
    "author": "L2T",
    'images': ['images/sms.jpeg', 'images/gateway.jpeg', 'images/gateway_access.jpeg','images/client.jpeg','images/send_sms.jpeg'],
    "description": "TunisieSMS description",
    "website": "https://www.tunisiesms.tn/",
    "category": "Tools",
    "demo": [],
    "data": [
        "data/sms_tunisiesms_setup_table_Gateway.xml",
        "security/groups.xml",
        "security/ir.model.access.csv",
        "serveraction_view.xml",
        "tunisiesms_actions.xml",
        "tunisiesms_view.xml",
        "tunisiesms_data.xml",
        "wizard/mass_sms_view.xml",
        "partner_sms_send_view.xml",
        "smstemplate_view.xml",
        "data/sms_tunisiesms_setup.xml",
        "data/sms_tunisiesms_setup_order.xml",
        "data/sms_tunisiesms_trigger_setup.xml",
        "data/sms_tunisiesms_setup_res_partner.xml",
        "data/send_sms_queue_cron.xml",
        "data/order_to_sms_queue_cron.xml",
        "data/get_dlr_status_cron.xml",
        "data/partner_to_sms_queue_cron.xml"
    ],
    "active": False,
    "installable": True,
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
