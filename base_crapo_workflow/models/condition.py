# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Condition(models.Model):
    """
    Condition definition
    """

    _name = "crapo.condition"
    _description = "Condition description"

    name = fields.Char(required=True)
    description = fields.Text(required=True)
    condition = fields.Char(required=True)

    is_precondition = fields.Boolean(required=True, default=True)
    is_postcondition = fields.Boolean(required=True, default=False)

    transition_id = fields.Many2one(
        string="Transition",
        comodel_name="crapo.transition",
        ondelete="cascade",
        required=True,
    )
