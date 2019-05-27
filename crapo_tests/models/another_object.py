# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AnObject(models.Model):
    _name = "crapo.test.another"
    _inherit = "crapo.business.object"
    _description = u"Another sample business Object"

    name = fields.Char(string="A Name")

    to_object = fields.Many2one(comodel_name="crapo.test.object")
