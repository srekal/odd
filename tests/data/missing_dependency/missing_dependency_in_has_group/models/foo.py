from odoo import models


class Foo(models.Model):
    _name = 'foo'

    def action_do_something(self):
        if self.env.user.has_group('website.some_group'):
            return 42
