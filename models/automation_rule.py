from odoo import models, fields

class AutomationRule(models.Model):
    _name = 'automation.rule'
    _description = 'Automation Rule'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

    model_id = fields.Many2one('ir.model')
    trigger = fields.Selection([
        ('cron', 'Scheduled'),
    ], default='cron')

    action_type = fields.Selection([
        ('create_invoice', 'Create Invoice'),
        ('create_po', 'Create Purchase Order')
    ])

    def run_automation(self):
        rules = self.search([('active', '=', True)])

        for rule in rules:
            if rule.action_type == 'create_invoice':
                self.env['sale.order'].auto_generate_invoice()

            elif rule.action_type == 'create_po':
                self.env['stock.automation'].auto_reorder()