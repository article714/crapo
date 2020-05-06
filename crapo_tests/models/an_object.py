"""
See README for details
"""
from odoo import models, fields


class AnObject(models.Model):
    """
    A simple sample object
    """

    _name = "crapo.test.object"
    _inherit = ["crapo.automaton.mixin"]
    _description = "A sample business Object"

    name = fields.Char()

    some_value = fields.Boolean()
