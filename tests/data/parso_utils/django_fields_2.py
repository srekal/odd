import django


class Foo(django.db.models.Model):
    _name = 'foo'
    _description = 'Foo'

    bar = django.fields.Many2one(
        String='Bar',
    )
