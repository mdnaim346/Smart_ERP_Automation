from odoo import models, fields, api

class AutomationRule(models.Model):
  _inherit= "sale.order"
  
  def auto_generate_invoice(self):
    orders= self.search([
      ('state','=','sale'),
      ('invoice_status','=','to invoice')
    ])
    
    for order in orders:
      invoice= order._create_invoices()
      invoice.action_post()