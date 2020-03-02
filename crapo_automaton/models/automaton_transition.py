from odoo import fields, models, exceptions, api, _


class CrapoAutomatonTransition(models.Model):
    """
    A transition between two states
    """

    _name = "crapo.automaton.transition"
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

    name = fields.Char(help="Transition's name", required=True)

    description = fields.Text()

    automaton_id = fields.Many2one(
        "crapo.automaton", required=True, ondelete="cascade"
    )

    model_id = fields.Many2one("ir.model", related="automaton_id.model_id")

    from_state_id = fields.Many2one(
        "crapo.automaton.state", ondelete="cascade", required=True,
    )

    to_state_id = fields.Many2one(
        "crapo.automaton.state", ondelete="cascade", required=True,
    )

    precondition_ids = fields.One2many(
        "crapo.automaton.condition",
        "transition_id",
        string="Pre-conditions",
        help=(
            "Conditions to be checked before "
            "initiating this transition. "
            "Evaluation environment contains 'record' which is a reference to"
            " the record to be checked, and 'env' which is a reference to "
            "odoo environment"
        ),
        domain=[("is_postcondition", "=", False)],
    )

    postcondition_ids = fields.One2many(
        "crapo.automaton.condition",
        "transition_id",
        string="Post-conditions",
        help=(
            "Conditions to be checked before ending this transition. "
            "Evaluation environment contains 'record' which is a "
            "reference to the record to be checked, and 'env' which "
            "is a reference to odoo environment"
        ),
        domain=[("is_postcondition", "=", True)],
    )

    action_id = fields.Many2one(
        "crapo.automaton.action", string="Action to be executed",
    )

    async_action = fields.Boolean(
        help="""Action will be run asynchronously, after transition is completed""",
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
        return super(CrapoAutomatonTransition, self).create(values)

    @api.multi
    def write(self, values):
        """
            Override to prevent save postcondtions on async_action
        """
        if values.get("async_action"):
            values["postcondition_ids"] = False

        return super(CrapoAutomatonTransition, self).write(values)
