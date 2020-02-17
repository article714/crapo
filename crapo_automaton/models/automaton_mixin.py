# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

from odoo.addons.crapo_automaton.mixins.crapo_readonly_view_mixin import (
    ReadonlyViewMixin,
)


class CrapoAutomatonMixin(ReadonlyViewMixin, models.Model):
    """
        Mixin class that can be used to define an Odoo Model eligible
        to be managed by a Crapo Automaton

        Should be use as a mixin class in existing objects
    """

    _name = "crapo.automaton.mixin"

    _description = """
    An object on which to  in a workflow, specific to a given model
    """
    _sync_state_field = ""

    _readonly_domain = (
        "[('crapo_readonly_fields', 'like', ',{},'.format(field_name))]"
    )
    _readonly_fields_to_add = ["crapo_readonly_fields"]

    crapo_automaton_id = fields.Many2one(
        "crapo.automaton",
        help="Automaton link to this model",
        default=lambda self: self._get_model_automaton(),
    )

    crapo_state_id = fields.Many2one(
        "crapo.automaton.state",
        help="""State in which this object is""",
        domain=lambda self: self._get_state_domain(),
        group_expand="_read_group_states",
        default=lambda self: self._get_default_state(),
    )

    crapo_readonly_fields = fields.Char(
        compute="_compute_crapo_readonly_fields", default=",0,"
    )

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

    # Computes automaton for current model
    @api.model
    def _get_model_automaton(self):
        automaton_model = self.env["crapo.automaton"]

        my_model = self.env["ir.model"].search(
            [("model", "=", self._name)], limit=1
        )
        my_automaton = automaton_model.search(
            [("model_id", "=", my_model.id)], limit=1
        )

        if my_automaton:
            return my_automaton
        else:
            return automaton_model.create(
                {
                    "name": "Automaton for {}".format(self._name),
                    "model_id": my_model.id,
                }
            )

    # State Management
    def _get_state_domain(self, domain=None):
        result = []

        if self.crapo_automaton_id:
            result.append(("automaton_id", "=", self.crapo_automaton_id.id))
        else:
            result.append(
                ("automaton_id", "=", self._get_model_automaton().id)
            )

        return result

    def _get_default_state(self):
        domain = self._get_state_domain()
        state_model = self.env["crapo.automaton.state"]
        automaton = self._get_model_automaton()

        if automaton:
            domain.append("|")
            domain.append(("is_start_state", "=", True))
            domain.append(("default_state", "=", 1))

        default_state = state_model.search(domain, limit=1)

        if default_state:
            return default_state
        elif automaton:
            return state_model.create(
                {"name": "New", "automaton_id": automaton.id}
            )
        else:
            return False

    def _next_states(self):
        self.ensure_one()
        domain = self._get_state_domain()

        next_states = False
        if self.crapo_automaton_id:
            eligible_transitions = self.env[
                "crapo.automaton.transition"
            ].search(
                [
                    ("automaton_id", "=", self.crapo_automaton_id.id),
                    ("from_state_id", "=", self.crapo_state_id.id),
                ]
            )

            target_ids = eligible_transitions.mapped(
                lambda x: x.to_state_id.id
            )

            if target_ids:
                domain.append(("id", "in", target_ids))

                next_states = self.env["crapo.automaton.state"].search(domain)

        else:
            domain.append(("sequence", ">", self.crapo_state_id.sequence))
            next_states = self.env["crapo.automaton.state"].search(
                domain, limit=1
            )

        return next_states

    def _read_group_states(self, states, domain, order):
        search_domain = self._get_state_domain(domain=domain)
        state_ids = states._search(
            search_domain, order=order, access_rights_uid=SUPERUSER_ID
        )
        return states.browse(state_ids)

    # =================
    # Write / Create
    # =================
    @api.model
    def create(self, values):
        rec = super(CrapoAutomatonMixin, self).create(values)

        if not self.env.context.get("crapo_no_creation_state_validation"):
            state_id = rec.crapo_state_id
            if not (state_id.is_start_state or state_id.is_creation_state):
                ir_model = self.env["ir.model"]
                raise ValidationError(
                    _(
                        """ "{}" is not a possible state to create a record of "{}" """
                    ).format(
                        state_id.display_name,
                        ir_model.browse(
                            ir_model._get_id(rec._name)
                        ).display_name,
                    )
                )
        return rec

    @api.multi
    def write(self, values):
        """
            Override write method in order to preventing transitioning
            to a non eligible state
        """
        # Look for a change of state
        target_state_id = None
        result = True

        if "crapo_state_id" in values:
            target_state_id = values["crapo_state_id"]

        # check if there is a change state needed
        if target_state_id is not None:
            # Search for elected transition
            transition = self._get_transition(target_state_id)

            if transition:
                result = True

                if transition.write_before:
                    result = super(CrapoAutomatonMixin, self).write(values)

                self.exec_conditions(transition.precondition_ids, "Pre")
                self.exec_action(transition.action, transition.async_action)
                self.exec_conditions(transition.postcondition_ids, "Post")

                # Return now if write has already been done
                if transition.write_before:
                    return result

        return super(CrapoAutomatonMixin, self).write(values)

    def _get_transition(self, target_state_id):
        """
            Retrieve transition between two state
        """
        # Check if next state is valid
        current_state = False
        for rec in self:
            next_states = rec._next_states()
            if rec.crapo_state_id.id == target_state_id:
                current_state = rec.crapo_state_id
                continue
            elif not next_states:
                raise ValidationError(
                    _("No target state is elegible for transitionning")
                )
            elif target_state_id not in next_states.ids:
                raise ValidationError(
                    _('State "{}" is not in eligible target states').format(
                        self.env["crapo.automaton.state"]
                        .browse(target_state_id)
                        .display_name
                        if target_state_id
                        else target_state_id
                    )
                )
            elif (
                current_state is not False
                and current_state != rec.crapo_state_id
            ):
                raise ValidationError(
                    _("Transitionning is not possible from differents states")
                )
            else:
                current_state = rec.crapo_state_id

        # Search for elected transition
        transition = self.env["crapo.automaton.transition"].search(
            [
                ("from_state_id", "=", current_state.id),
                ("to_state_id", "=", target_state_id),
            ],
            limit=1,
        )

        return transition

    def exec_conditions(self, condition_ids, prefix):
        """
            Execute Pre/Postconditions.

            condition_ids: must be a crapo.automaton.condition object
            prefix: a string to indicate if it's pre or post conditions
        """

        if condition_ids:
            for rec in self:
                for condition_id in condition_ids:
                    try:
                        is_valid = safe_eval(
                            condition_id.condition,
                            {"object": rec, "env": self.env},
                        )
                    except Exception as err:
                        logging.error(
                            "CRAPO: Failed to validate transition"
                            " %sconditions: %s",
                            prefix,
                            str(err),
                        )
                        is_valid = False

                    # Raise an error if not valid
                    if not is_valid:
                        raise ValidationError(
                            _(
                                "Invalid {}-conditions for Object: {} \n"
                                "{}condition: {} failed \n"
                                "Details: {}"
                            ).format(
                                prefix,
                                rec.display_name,
                                prefix,
                                condition_id.name,
                                condition_id.description,
                            )
                        )

    def exec_action(self, action, async_action):
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
