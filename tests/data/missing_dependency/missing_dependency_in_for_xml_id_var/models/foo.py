from odoo import models


class Foo(models.Model):
    _name = 'foo'

    def action_do_something(self):
        record_id = 'some_action'
        return self.env['ir.actions.act_window'].for_xml_id('account', record_id)
