# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CrapoAutomatonCondition(models.Model):
    """
    Condition definition
    """

    _name = "crapo.automaton.condition"
    _description = "Condition description"
    _order = "sequence, name"

    name = fields.Char(required=True)
    description = fields.Text(
        help="Message that will be show to user when this conditions is not met",
        required=True,
    )

    condition = fields.Char(
        help="Available object: env, record", required=True
    )

    is_postcondition = fields.Boolean(required=True, default=False)

    sequence = fields.Integer(
        help="Sequence define in which order condition will be evaluated",
        required=True,
        default=1,
    )

    transition_id = fields.Many2one(
        "crapo.automaton.transition",
        string="Transition",
        ondelete="cascade",
        required=True,
    )
