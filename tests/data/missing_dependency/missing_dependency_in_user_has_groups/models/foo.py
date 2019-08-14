from odoo import models


class Foo(models.Model):
    _name = 'foo'

    def action_do_something(self):
        if self.env['foo'].user_has_groups('missing_dependency_in_user_has_groups.some_group,!project.another_group'):
            return 42
