from odoo import http


class Controller(http.Controller):
    @http.route
    def index(self, *args, **kwargs):
        return "Foo"
