# ©2019- Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WorkflowTransition(models.Model):
    """
    A transition between two Workflow activities
    """

    _name = "crapo.workflow.transition"
    _description = "Transition between two activities"

    name = fields.Char(help="Transition's name", required=True, size=32,)

    description = fields.Text(size=256)

    workflow_id = fields.Many2one(
        "crapo.workflow",
        related="activity_id.workflow_id",
        store=True,
        required=True,
    )

    activity_id = fields.Many2one(
        "crapo.workflow.activity", string="From activity", required=True,
    )

    joiner_id = fields.Many2one(
        "crapo.workflow.joiner", string="To joiner", required=True,
    )

    condition = fields.Char(
        help="""Conditions to be checked before
 initiating this transition.

Evaluation environment contains 'object' which is a reference to the object
to be checked, and 'env' which is a reference to odoo environment""",
    )
