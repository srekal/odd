from odoo import fields, models


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    other = fields.Many2one(
        comodel_name='baz',
        required_if_provider="foo",
    )
