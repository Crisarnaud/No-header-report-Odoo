import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"