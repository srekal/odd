from odoo import models
from odoo.addons.base.models.qweb import QWeb


class IrQWeb(models.AbstractModel, QWeb):
    _name = 'ir.qweb'
    _description = 'Qweb'
