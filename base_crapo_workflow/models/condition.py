# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _, api, exceptions

class Condition(models.Model):
    """
    Condition definition
    """
    _name = "crapo.condition"
    _description = "Condition description"

    name = fields.Char(
        string="Name",
        required=True
    )
    description = fields.Text(
        string="Condition description",
        required=True
    )
    condition = fields.Char(
        string="Condition eval",
        required=True
    )

    transition_id = fields.Many2one(
        string="Transition",
        comodel_name="crapo.transition",
        ondelete="cascade",
        required=True
    )