import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class AutomationRule(models.Model):
    _name = 'automation.rule'
    _description = 'Automation Rule'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
    )
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        required=True,
    )

    model_id = fields.Many2one('ir.model', string='Applies To', readonly=True)
    trigger = fields.Selection([
        ('cron', 'Scheduled'),
        ('manual', 'Manual'),
    ], default='cron', required=True)

    action_type = fields.Selection([
        ('create_invoice', 'Create Invoice'),
        ('create_po', 'Create Purchase Order')
    ], required=True)

    auto_post_invoice = fields.Boolean(default=True)
    max_records_per_run = fields.Integer(default=50)
    reorder_quantity = fields.Float(default=1.0)
    last_run_date = fields.Datetime(readonly=True)
    execution_count = fields.Integer(readonly=True)
    success_count = fields.Integer(readonly=True)
    failure_count = fields.Integer(readonly=True)
    log_ids = fields.One2many('automation.rule.log', 'rule_id', string='Logs')

    @api.onchange('action_type')
    def _onchange_action_type(self):
        for rule in self:
            rule.model_id = rule._get_default_model_for_action()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('action_type') and not vals.get('model_id'):
                vals['model_id'] = self._get_model_id_for_action(vals['action_type'])
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('action_type') and not vals.get('model_id'):
            vals['model_id'] = self._get_model_id_for_action(vals['action_type'])
        return super().write(vals)

    def _get_default_model_for_action(self):
        self.ensure_one()
        model_id = self._get_model_id_for_action(self.action_type)
        return model_id and self.env['ir.model'].browse(model_id)

    def _get_model_id_for_action(self, action_type):
        model_name = {
            'create_invoice': 'sale.order',
            'create_po': 'product.template',
        }.get(action_type)
        if not model_name:
            return False
        model = self.env['ir.model']._get(model_name)
        return model.id if model else False

    @api.model
    def run_automation(self):
        rules = self.search([('active', '=', True)])
        for rule in rules:
            rule.action_run_now()

    def action_run_now(self):
        for rule in self:
            rule._run_single_rule()
        return True

    def _run_single_rule(self):
        self.ensure_one()
        started_at = fields.Datetime.now()
        processed = 0
        skipped = 0
        failed = 0
        message = ''
        status = 'success'

        try:
            if self.action_type == 'create_invoice':
                result = self.env['sale.order'].auto_generate_invoice(
                    max_records=self.max_records_per_run,
                    auto_post=self.auto_post_invoice,
                    company=self.company_id,
                )
            elif self.action_type == 'create_po':
                result = self.env['product.template'].auto_reorder_products(
                    max_records=self.max_records_per_run,
                    reorder_quantity=self.reorder_quantity,
                    company=self.company_id,
                )
            else:
                result = {'processed': 0, 'skipped': 1, 'failed': 0, 'message': 'No action configured.'}

            processed = result.get('processed', 0)
            skipped = result.get('skipped', 0)
            failed = result.get('failed', 0)
            message = result.get('message', '')
            if failed:
                status = 'failed' if not processed else 'partial'
            elif skipped and not processed:
                status = 'skipped'
        except Exception as error:
            failed = 1
            status = 'failed'
            message = str(error)
            _logger.exception('Automation rule %s failed', self.display_name)

        self.env['automation.rule.log'].sudo().create({
            'rule_id': self.id,
            'status': status,
            'message': message,
            'processed_count': processed,
            'skipped_count': skipped,
            'failed_count': failed,
            'started_at': started_at,
            'finished_at': fields.Datetime.now(),
            'company_id': self.company_id.id,
        })
        self.write({
            'last_run_date': fields.Datetime.now(),
            'execution_count': self.execution_count + 1,
            'success_count': self.success_count + (1 if status in ('success', 'partial', 'skipped') else 0),
            'failure_count': self.failure_count + (1 if status == 'failed' else 0),
        })


class AutomationRuleLog(models.Model):
    _name = 'automation.rule.log'
    _description = 'Automation Rule Log'
    _order = 'started_at desc, id desc'
    _rec_name = 'rule_id'

    rule_id = fields.Many2one('automation.rule', required=True, ondelete='cascade')
    status = fields.Selection([
        ('success', 'Success'),
        ('partial', 'Partial'),
        ('skipped', 'Skipped'),
        ('failed', 'Failed'),
    ], required=True, default='success')
    message = fields.Text()
    processed_count = fields.Integer()
    skipped_count = fields.Integer()
    failed_count = fields.Integer()
    started_at = fields.Datetime(required=True)
    finished_at = fields.Datetime()
    company_id = fields.Many2one('res.company', required=True)
