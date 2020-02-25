# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AnObject(models.Model):
    _name = "crapo.test.object"
    _inherit = ["crapo.automaton.mixin"]
    _description = "A sample business Object"

    name = fields.Char()

    some_value = fields.Boolean()
