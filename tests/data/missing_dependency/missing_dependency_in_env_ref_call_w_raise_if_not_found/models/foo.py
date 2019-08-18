from odoo import models


class Foo(models.Model):
    _name = 'foo'

    def action_do_something(self):
        record = self.env.ref('sale.some_record', raise_if_not_found=False)
        if record:
            record.unlink()
        return {}
