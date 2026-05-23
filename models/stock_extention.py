from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    min_qty = fields.Float(string="Minimum Quantity")

    def auto_reorder_products(self, max_records=50, reorder_quantity=1.0, company=False):
        domain = [('min_qty', '>', 0), ('purchase_ok', '=', True)]
        if company:
            domain.append('|')
            domain.append(('company_id', '=', False))
            domain.append(('company_id', '=', company.id))

        limit = max_records if max_records and max_records > 0 else None
        products = self.search(domain, limit=limit, order='name asc, id asc')
        processed = 0
        skipped = 0
        failed = 0
        messages = []

        PurchaseOrder = self.env['purchase.order']
        PurchaseOrderLine = self.env['purchase.order.line']

        for product in products:
            try:
                if product.qty_available >= product.min_qty:
                    skipped += 1
                    continue

                variant = product.product_variant_id
                if not variant:
                    skipped += 1
                    messages.append('%s skipped: no product variant found.' % product.display_name)
                    continue

                seller = product.seller_ids[:1]
                if not seller:
                    skipped += 1
                    messages.append('%s skipped: no vendor configured.' % product.display_name)
                    continue

                existing_line = PurchaseOrderLine.search([
                    ('product_id', '=', variant.id),
                    ('order_id.partner_id', '=', seller.name.id),
                    ('order_id.state', 'in', ['draft', 'sent']),
                ], limit=1)
                if existing_line:
                    skipped += 1
                    messages.append('%s skipped: draft RFQ already exists.' % product.display_name)
                    continue

                quantity = max(reorder_quantity or 0.0, product.min_qty - product.qty_available)
                if quantity <= 0:
                    skipped += 1
                    continue

                order = PurchaseOrder.create({
                    'partner_id': seller.name.id,
                    'company_id': company.id if company else self.env.company.id,
                    'origin': 'Smart ERP Automation',
                })
                PurchaseOrderLine.create({
                    'order_id': order.id,
                    'product_id': variant.id,
                    'name': variant.display_name,
                    'product_qty': quantity,
                    'product_uom': variant.uom_po_id.id or variant.uom_id.id,
                    'price_unit': seller.price or variant.standard_price,
                    'date_planned': fields.Datetime.now(),
                })
                processed += 1
                messages.append('%s: RFQ %s created.' % (product.display_name, order.name))
            except Exception as error:
                failed += 1
                messages.append('%s failed: %s' % (product.display_name, error))

        return {
            'processed': processed,
            'skipped': skipped,
            'failed': failed,
            'message': '\n'.join(messages) or 'No products need reordering.',
        }
