from odoo import models


class Foo(models.Model):
    _name = 'foo'

    def action_do_something(self):
        if self.env['res.users'].has_group('hr.some_group'):
            return 42
