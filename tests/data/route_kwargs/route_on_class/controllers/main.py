from odoo import http


@http.route("/index", type="http", auth="public", foo="bar")
class Controller(http.Controller):
    def index(self, *args, **kwargs):
        return "Foo"
