{
    'name': 'CRM Lead Tracking Log',
    'version': '1.0',
    'summary': 'Track salesperson location via external API when creating CRM leads',
    'category': 'CRM',
    'depends': ['crm'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/crm_lead_tracking_log_views.xml',
        'data/tracking_notification_cron.xml',
    ],
    'application': True,
}