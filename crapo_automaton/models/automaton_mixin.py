from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

from ..mixins.crapo_readonly_view_mixin import ReadonlyViewMixin


class CrapoAutomatonMixin(ReadonlyViewMixin, models.AbstractModel):
    """
        Mixin class that can be used to define an Odoo Model eligible
        to be managed by a Crapo Automaton

        Should be use as a mixin class in existing objects
    """

    _name = "crapo.automaton.mixin"

    _description = "Crapo automaton mixin"

    _readonly_domain = (
        "[('crapo_readonly_fields', 'like', ',{},'.format(field_name))]"
    )
    _readonly_fields_to_add = ["crapo_readonly_fields"]

    crapo_automaton_id = fields.Many2one(
        "crapo.automaton",
        help="Automaton link to this model",
        default=lambda self: self._crapo_get_model_automaton(),
    )

    crapo_state_id = fields.Many2one(
        "crapo.automaton.state",
        help="""State in which this object is""",
        default=lambda self: self._crapo_get_model_automaton().default_state_id,
        domain=lambda self: [
            (
                "automaton_id",
                "=",
                (
                    self.crapo_automaton_id
                    or self._crapo_get_model_automaton()
                ).id,
            )
        ],
        group_expand="_read_group_crapo_states",
    )

    crapo_readonly_fields = fields.Char(
        compute="_compute_crapo_readonly_fields", default=",0,"
    )

    def _read_group_crapo_states(self, states, domain, order):
        state_ids = states._search(
            domain, order=order, access_rights_uid=SUPERUSER_ID
        )
        return states.browse(state_ids)

    @api.depends("crapo_state_id")
    @api.onchange("crapo_state_id")
    def _compute_crapo_readonly_fields(self):
        for rec in self:
            if rec.crapo_state_id.readonly_fields:
                rec.crapo_readonly_fields = ",{},".format(
                    rec.crapo_state_id.readonly_fields
                )
            else:
                rec.crapo_readonly_fields = ",0,"

    @api.model
    def _crapo_get_model_automaton(self):
        """
            Get automaton linked to this model if there is one
        """
        domain = [("model_id", "=", self.env["ir.model"]._get_id(self._name))]
        return self.env["crapo.automaton"].search(domain, limit=1)

    def _crapo_get_sync_state(self, id_sync_field):
        """
            Return crapo.state linked to id_sync_field
        """
        automaton = self.mapped("crapo_automaton_id")
        sync_state = automaton.state_ids.filtered(
            lambda state: state.sync_state_id == id_sync_field
        )
        # If no crapo sate is link to sync_state_field value
        if not sync_state:
            sync_rec = self.env[
                self.env[automaton.model_id.model]
                ._fields[automaton.sync_state_field]
                .comodel_name
            ].browse(id_sync_field)

            raise ValidationError(
                _(
                    "No crapo state is linked to: {} ({}) on crapo automaton: {}"
                ).format(
                    sync_rec, sync_rec.display_name, automaton.display_name,
                )
            )
        return sync_state

    # =================
    # Write / Create
    # =================
    @api.model
    def create(self, values):
        rec = super(CrapoAutomatonMixin, self).create(values)

        automaton = rec.crapo_automaton_id
        if automaton:

            # Sync crapo state with sync_state_field if needed
            if automaton.sync_state_field:
                rec.with_context(
                    {"crapo_no_transition": True}
                ).crapo_state_id = rec._crapo_get_sync_state(
                    rec[automaton.sync_state_field].id
                ).id

            state_id = rec.crapo_state_id
            # Case where no crapo state value is define
            if not state_id:
                raise ValidationError(
                    _(
                        "{} is required. HINT: Define a default crapo state"
                    ).format(self._fields["crapo_state_id"].string)
                )

            # Check if defined crapo state is a possible create value
            if not self.env.context.get(
                "crapo_no_creation_state_validation"
            ) and not (state_id.is_start_state or state_id.is_creation_state):
                raise ValidationError(
                    _(
                        ' "{}" is not a possible crapo state '
                        ' to create a record of "{}" '
                    ).format(
                        state_id.display_name, rec._name,
                    )
                )
        return rec

    @api.multi
    def write(self, values):
        """
            Override write method in order to preventing transitioning
            to a non eligible state
        """

        # Skip transition process
        if self.env.context.get("crapo_no_transition"):
            return super(CrapoAutomatonMixin, self).write(values)

        automaton = self.mapped("crapo_automaton_id")
        if automaton:
            # Sync crapo state with sync_state_field if needed
            if automaton.sync_state_field in values:
                values["crapo_state_id"] = self._crapo_get_sync_state(
                    values[automaton.sync_state_field]
                ).id

            # Check if there is a change state needed
            if values.get("crapo_state_id"):
                target_state_id = self.env["crapo.automaton.state"].browse(
                    values["crapo_state_id"]
                )
                # Search for elected transition
                for rec in self:
                    transition = automaton.transition_ids.filtered(
                        lambda trans: trans.from_state_id == rec.crapo_state_id
                        and trans.to_state_id == target_state_id
                    )
                    if not transition:
                        if rec.crapo_state_id == target_state_id:
                            continue

                        raise ValidationError(
                            _(
                                'State "{}" is not in eligible '
                                'target state from state "{}"'
                            ).format(
                                target_state_id.display_name,
                                rec.crapo_state_id.display_name,
                            )
                        )

                    if transition.write_before:
                        result = super(CrapoAutomatonMixin, rec).write(values)

                    rec._crapo_exec_conditions(
                        transition.precondition_ids, "Pre"
                    )
                    rec._crapo_exec_action(
                        transition.action_id, transition.async_action
                    )
                    rec._crapo_exec_conditions(
                        transition.postcondition_ids, "Post"
                    )

                # Return now if write has already been done
                if transition.write_before:
                    return result

        return super(CrapoAutomatonMixin, self).write(values)

    def _crapo_exec_conditions(self, condition_ids, prefix):
        """
            Execute Pre/Postconditions.

            condition_ids: must be a crapo.automaton.condition object
            prefix: a string to indicate if it's pre or post conditions
        """

        if not condition_ids:
            return

        for condition_id in condition_ids:
            is_valid = safe_eval(
                condition_id.condition, {"record": self, "env": self.env},
            )

            # Raise an error if not valid
            if not is_valid:
                raise ValidationError(
                    _(
                        "Invalid {}-conditions for record: {} \n"
                        "{}condition: {} \n"
                        "Details: {}"
                    ).format(
                        prefix,
                        self.display_name,
                        prefix,
                        condition_id.name,
                        condition_id.description,
                    )
                )

    def _crapo_exec_action(self, action, async_action):
        if action:
            context = {
                "active_model": self._name,
                "active_id": self.id,
                "active_ids": self.ids,
            }
            if async_action:
                action.with_context(context).with_delay().run_async()
            else:
                action.with_context(context).run()
