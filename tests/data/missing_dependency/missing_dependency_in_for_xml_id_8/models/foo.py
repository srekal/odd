from openerp import models


class Foo(models.Model):
    _name = 'foo'

    def action_do_something(self, cr, uid, context=None):
        return self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'stock', 'some_action', context)
