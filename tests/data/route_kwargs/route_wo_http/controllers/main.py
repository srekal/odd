from odoo import http
from odoo.http import route


class Controller(http.Controller):
    @route("/index", type="http", auth="public")
    def index(self, *args, **kwargs):
        return "Foo"
