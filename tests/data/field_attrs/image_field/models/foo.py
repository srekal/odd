from odoo import fields, models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    image_128 = fields.Image(
        max_width=128,
        max_height=128,
    )
