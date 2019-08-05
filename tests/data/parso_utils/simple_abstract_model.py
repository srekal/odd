from odoo import models


class BaseFoo(models.AbstractModel):
    _name = 'afoo'
    _description = 'Foo (abstract)'
