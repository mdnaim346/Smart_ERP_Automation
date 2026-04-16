from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Compatibility field for environments where a settings view
    # references the Mapbox token but the owning module field is unavailable.
    map_box_token = fields.Char(
        string="Token Map Box",
        config_parameter="web_map.token_map_box",
    )

    # Compatibility field for settings views coming from sale_stock.
    default_picking_policy = fields.Selection(
        [
            ("direct", "Ship products as soon as available, with back orders"),
            ("one", "Ship all products at once"),
        ],
        string="Picking Policy",
        default="direct",
        default_model="sale.order",
        required=True,
    )
