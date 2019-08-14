from odoo import models


class Foo(models.Model):
    _name = 'foo'

    def action_do_something(self):
        self.env.ref('sale.some_record').unlink()
        return {}
