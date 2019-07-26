from odoo import http


class Controller(http.Controller):
    @http.foo("/index", type="http", auth="public", bar="baz")
    def index(self, *args, **kwargs):
        return "Foo"
