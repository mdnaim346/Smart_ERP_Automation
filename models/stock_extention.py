from odoo import models, api, fields

class ProductTemplate(models.Model):
  _inherit="product.template"
  
  min_qty = fields.Float(string= " Minimum Quantity")
  
  
class StockAutomation(models.Model):
  _name= "stock.automation"
  
  def auto_reorder(self):
    products= self.env['product.template'].search([])
    
    for product in products:
      if product.qty_available < product.min_qty:
        self.env['purchase.order'].create({'partner_id': product.seller_ids[0].name.id}) 
  