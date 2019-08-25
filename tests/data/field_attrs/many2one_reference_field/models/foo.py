from odoo import fields, models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    res_model_id = fields.Many2one(
        comodel_name='ir.model',
    )
    res_model = fields.Char(
        related='res_model_id.model',
    )
    res_id = fields.Many2oneReference(
        index=True,
        required=True,
        model_field='res_model',
    )
