# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, exceptions, api, _


class StateMachineTransition(models.Model):
    """
    A transition between two states
    """

    _name = "crapo.transition"
    _description = "Transition between two states"

    @api.constrains("postconditions", "async_action")
    def async_action_post_conditions_conflict(self):
        """
            Checks that no post-condition is set when using an async action
        """
        for rec in self:
            if rec.async_action and rec.postconditions:
                raise exceptions.ValidationError(
                    _("Transition can't have async action and postcontitions")
                )

    name = fields.Char(
        help="Transition's name", required=True, translate=True, size=32
    )

    description = fields.Text(required=False, translate=True, size=256)

    automaton = fields.Many2one(
        comodel_name="crapo.automaton", store=True, required=True, index=True,
    )

    model_id = fields.Many2one(
        string="Model", comodel_name="ir.model", related="automaton.model_id"
    )

    from_state = fields.Many2one(
        comodel_name="crapo.state",
        ondelete="cascade",
        required=True,
        index=True,
    )

    to_state = fields.Many2one(
        comodel_name="crapo.state",
        ondelete="cascade",
        required=True,
        index=True,
    )

    precondition_ids = fields.One2many(
        "crapo.condition",
        "transition_id",
        string="Pre-conditions",
        help=(
            "Conditions to be checked before "
            "initiating this transition. "
            "Evaluation environment contains 'object' which is a reference to"
            " the object to be checked, and 'env' which is a reference to "
            "odoo environment"
        ),
        required=False,
        domain=[("is_precondition", "=", True)],
    )

    postcondition_ids = fields.One2many(
        "crapo.condition",
        "transition_id",
        string="Post-conditions",
        help=(
            "Conditions to be checked before ending this transition. "
            "Evaluation environment contains 'object' which is a "
            "reference to the object to be checked, and 'env' which "
            "is a reference to odoo environment"
        ),
        required=False,
        domain=[("is_postcondition", "=", True)],
    )

    action = fields.Many2one(
        string="Action to be executed",
        comodel_name="crapo.action",
        required=False,
    )

    async_action = fields.Boolean(
        help="""Action will be run asynchronously, after transition
                                  is completed""",
        default=False,
    )

    write_before = fields.Boolean(
        string="Write Object before",
        help="""
All updates to object will be commited before transitioning

This is useful for transitions where preconditions needs to be
tested with values that might have either changed together with the state
change or during the write process (computed fields) """,
        default=False,
    )

    @api.model
    def create(self, values):
        """
           Override to prevent save postcondtions on async_action
        """
        if values.get("async_action"):
            values["postcondition_ids"] = False
        return super(StateMachineTransition, self).create(values)

    @api.multi
    def write(self, values):
        """
            Override to prevent save postcondtions on async_action
        """
        if values.get("async_action"):
            values["postcondition_ids"] = False

        return super(StateMachineTransition, self).write(values)