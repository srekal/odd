from odoo import http


class Controller(http.Controller):
    @http.route("/index", type="http", auth="public")
    def index(self, *args, **kwargs):
        return "Foo"
