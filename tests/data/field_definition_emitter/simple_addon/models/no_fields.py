from collections import defaultdict

from odoo import models


class NoFields(models.Model):
    _name = 'no.fields'
    _description = 'No Fields'

    cache = defaultdict(list)
