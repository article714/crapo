"""
See README for details
"""
from odoo import fields, models, _, api, exceptions


class CrapoAutomatonState(models.Model):
    """
    A state used in the context of an automaton
    """

    _name = "crapo.automaton.state"
    _description = "State in a workflow, specific to a given model"
    _order = "sequence, name"

    name = fields.Char(help="State's name", required=True)

    description = fields.Text()

    automaton_id = fields.Many2one(
        "crapo.automaton", required=True, ondelete="cascade"
    )

    sequence = fields.Integer(
        default=1,
        help="Sequence gives the order in which states are displayed",
    )

    default_state = fields.Boolean(
        help="Might be use as default state.", default=False, store=True
    )

    transitions_to_ids = fields.One2many(
        "crapo.automaton.transition",
        "to_state_id",
        string="Incoming transitions",
    )

    transitions_from_ids = fields.One2many(
        "crapo.automaton.transition",
        "from_state_id",
        string="Outgoing transitions",
    )

    # computed field to identify start and end states
    is_start_state = fields.Boolean(
        "Start State",
        compute="_compute_is_start_end_state",
        store=True,
        index=True,
    )

    is_end_state = fields.Boolean(
        "End State",
        compute="_compute_is_start_end_state",
        store=True,
        index=True,
    )

    is_creation_state = fields.Boolean(
        help="""Indicate if this state is a possible state to create a record.
        This value is not take in account if it's a start state""",
        default=False,
    )

    readonly_fields = fields.Char(
        help="""List of model's fields name separated by comma that
                will be readonly when records are in this state"""
    )

    sync_state_id = fields.Integer(
        help="sync state field id that is link to this state"
    )

    # =================================
    # Compute
    # =================================

    @api.depends("transitions_to_ids", "transitions_from_ids")
    def _compute_is_start_end_state(self):
        for record in self:
            record.is_start_state = not record.transitions_to_ids
            record.is_end_state = not record.transitions_from_ids

    # ====================================
    # Write / Create
    # ====================================

    @api.model
    def create(self, values):
        """
            Write crapo_state_id on automaton.model_id existing records if
            there a sync_state_field on automaton
        """
        rec = super(CrapoAutomatonState, self).create(values)

        automaton = rec.automaton_id
        model = self.env[automaton.model_id.model]

        # Synchronize existing automaton.model_id records
        if automaton.sync_state_field:
            model.search(
                [(automaton.sync_state_field, "=", rec.sync_state_id)]
            ).with_context({"crapo_no_transition": True}).write(
                {"crapo_state_id": rec.id}
            )

        return rec

    @api.multi
    def write(self, values):
        """
            Override default method to prevent multi default state
        """
        if "default_state" in values:
            if values["default_state"]:
                if len(self) > 1:
                    raise exceptions.ValidationError(
                        _("There should be only one default state per model")
                    )
                else:
                    # Reset previous default value if there is one
                    if self.automaton_id.default_state_id:
                        self.automaton_id.default_state_id.default_state = (
                            False
                        )

        return super(CrapoAutomatonState, self).write(values)
