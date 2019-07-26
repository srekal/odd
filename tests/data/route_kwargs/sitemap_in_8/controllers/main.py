from openerp import http


class Controller(http.Controller):
    @http.route("/index", type="http", auth="public", sitemap=False)
    def index(self, *args, **kwargs):
        return "Foo"
