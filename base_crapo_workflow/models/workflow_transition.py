# ©2019- Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _, api


class WorkflowTransition(models.Model):
    """
    A transition between two Workflow activities
    """

    _name = "crapo.workflow.transition"
    _description = "Transition between two activities"

    name = fields.Char(
        string="Name",
        help="Transition's name",
        required=True,
        translate=True,
        size=32,
    )

    description = fields.Text(
        string=u"Description", required=False, translate=True, size=256
    )

    workflow = fields.Many2one(
        string="Automaton",
        comodel_name="crapo.workflow",
        related="from_activity.workflow",
        store=True,
        required=True,
        index=True,
    )

    from_activity = fields.Many2one(
        string="From activity",
        comodel_name="crapo.workflow.activity",
        ondelete="cascade",
        required=True,
        index=True,
    )

    to_activity = fields.Many2one(
        string="To activity",
        comodel_name="crapo.workflow.activity",
        ondelete="cascade",
        required=True,
        index=True,
    )

    transition_kind = fields.Selection(
        [
            ("event", "Event triggered"),
            (
                "auto",
                "Automatic when activity ended and preconditions are met",
            ),
        ],
        required=True,
        default="auto",
    )

    preconditions = fields.Char(
        string="Pre-conditions",
        help="""Conditions to be checked before
 initiating this transition.

Evaluation environment contains 'object' which is a reference to the object
to be checked, and 'env' which is a reference to odoo environment""",
        required=False,
    )
