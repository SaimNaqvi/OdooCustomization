from odoo import models, fields


class FOBPoint(models.Model):
    _name = 'fob.point'

    name = fields.Char(string='Point Name', required=True)


class ShipVia(models.Model):
    _name = 'ship.via'

    name = fields.Char(string='Ship Name', required=True)