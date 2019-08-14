from odoo import models


class Foo(models.Model):
    _name = 'foo'

    def action_do_something(self):
        return self.env['ir.actions.act_window'].for_xml_id('account', 'some_action')
