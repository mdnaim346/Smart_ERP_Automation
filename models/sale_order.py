from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def auto_generate_invoice(self, max_records=50, auto_post=True, company=False):
        domain = [
            ('state', '=', 'sale'),
            ('invoice_status', '=', 'to invoice'),
        ]
        if company:
            domain.append(('company_id', '=', company.id))

        limit = max_records if max_records and max_records > 0 else None
        orders = self.search(domain, limit=limit, order='date_order asc, id asc')
        processed = 0
        skipped = 0
        failed = 0
        messages = []

        for order in orders:
            try:
                invoiceable_lines = order.order_line.filtered(lambda line: not line.display_type and line.qty_to_invoice > 0)
                if not invoiceable_lines:
                    skipped += 1
                    messages.append('%s skipped: no invoiceable lines.' % order.name)
                    continue

                invoices = order._create_invoices()
                if not invoices:
                    skipped += 1
                    messages.append('%s skipped: no invoice was created.' % order.name)
                    continue

                if auto_post:
                    invoices.filtered(lambda move: move.state == 'draft').action_post()
                processed += len(invoices)
                messages.append('%s: %s invoice(s) created.' % (order.name, len(invoices)))
            except Exception as error:
                failed += 1
                messages.append('%s failed: %s' % (order.name, error))

        return {
            'processed': processed,
            'skipped': skipped,
            'failed': failed,
            'message': '\n'.join(messages) or 'No sale orders found for invoicing.',
        }
