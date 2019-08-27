# coding: utf-8

# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import fields, api, exceptions, _
from odoo import SUPERUSER_ID
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base_crapo_workflow.mixins.crapo_readonly_view_mixin import (
    ReadonlyViewMixin,
)


class ObjectWithStateMixin(ReadonlyViewMixin):
    """
        Mixin class that can be used to define an Odoo Model eligible
        to be managed by a Crapo Automaton

        Should be use as a mixin class in existing objects
    """

    _readonly_domain = (
        "[('crapo_readonly_fields', 'like', ',{},'.format(field_name))]"
    )
    _readonly_fields_to_add = ["crapo_readonly_fields"]

    automaton = fields.Many2one(
        comodel_name="crapo.automaton",
        string="Related automaton",
        help=(
            "The automaton describes the various transitions "
            "an object can go through between states."
        ),
        default=lambda self: self._get_model_automaton(),
        store=True,
        index=True,
        required=True,
    )

    state = fields.Many2one(
        comodel_name="crapo.state",
        help="""State in which this object is""",
        track_visibility="onchange",
        domain=lambda self: self._get_state_domain(),
        group_expand="_read_group_states",
        default=lambda self: self._get_default_state(),
        store=True,
        index=True,
        required=True,
    )

    crapo_readonly_fields = fields.Char(
        compute="_compute_crapo_readonly_fields", default=",0,"
    )

    @api.depends("state")
    @api.onchange("state")
    def _compute_crapo_readonly_fields(self):
        for rec in self:
            if rec.state.readonly_fields:
                rec.crapo_readonly_fields = ",{},".format(
                    rec.state.readonly_fields
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

        if self.automaton:
            result.append(("automaton", "=", self.automaton.id))
        else:
            result.append(("automaton", "=", self._get_model_automaton().id))

        return result

    def _get_default_state(self):
        domain = self._get_state_domain()
        state_model = self.env["crapo.state"]
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
                {"name": "New", "automaton": automaton.id}
            )
        else:
            return False

    def _next_states(self):
        self.ensure_one()
        domain = self._get_state_domain()

        next_states = False
        if self.automaton:
            eligible_transitions = self.env["crapo.transition"].search(
                [
                    ("automaton", "=", self.automaton.id),
                    ("from_state", "=", self.state.id),
                ]
            )

            target_ids = eligible_transitions.mapped(lambda x: x.to_state.id)

            if target_ids:
                domain.append(("id", "in", target_ids))

                next_states = self.env["crapo.state"].search(domain)

        else:
            domain.append(("sequence", ">", self.state.sequence))
            next_states = self.env["crapo.state"].search(domain, limit=1)

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
    @api.multi
    def write(self, values):
        """
            Override write method in order to preventing transitioning
            to a non eligible state
        """
        # Look for a change of state
        target_state_id = None
        result = True

        if "state" in values:
            target_state_id = values["state"]

        # check if there is a change state needed
        if target_state_id is not None:
            # Search for elected transition
            transition = self._get_transition(target_state_id)

            if transition:
                result = True

                if transition.write_before:
                    result = super(ObjectWithStateMixin, self).write(values)

                self.exec_conditions(transition.preconditions, "Pre")
                self.exec_action(transition.action, transition.async_action)
                self.exec_conditions(transition.postconditions, "Post")

                # Return now if write has already been done
                if transition.write_before:
                    return result

        return super(ObjectWithStateMixin, self).write(values)

    def _get_transition(self, target_state_id):
        """
            Retrieve transition between two state
        """
        # Check if next state is valid
        current_state = False
        for rec in self:
            next_states = rec._next_states()
            if rec.state.id == target_state_id:
                current_state = rec.state
                continue
            elif not next_states:
                raise exceptions.ValidationError(
                    _("No target state is elegible for transitionning")
                )
            elif target_state_id not in next_states.ids:
                raise exceptions.ValidationError(
                    _("State is not in eligible target states")
                )
            elif current_state is not False and current_state != rec.state:
                raise exceptions.ValidationError(
                    _("Transitionning is not possible from differents states")
                )
            else:
                current_state = rec.state

        # Search for elected transition
        transition = self.env["crapo.transition"].search(
            [
                ("from_state", "=", current_state.id),
                ("to_state", "=", target_state_id),
            ],
            limit=1,
        )

        return transition

    def exec_conditions(self, conditions, prefix):
        """
            Execute Pre/Postconditions.

            conditions: must be a safe_eval expression
            prefix: a string to indicate if it's pre or post conditions
        """
        if conditions:
            for rec in self:
                try:
                    is_valid = safe_eval(
                        conditions, {"object": rec, "env": self.env}
                    )
                except Exception as err:
                    logging.error(
                        "CRAPO: Failed to validate transition %sconditions: %s",
                        prefix,
                        str(err),
                    )
                    is_valid = False

                # Raise an error if not valid
                if not is_valid:
                    raise exceptions.ValidationError(
                        _("Invalid {}-conditions for Object: {}").format(
                            prefix, rec.display_name
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
                action.with_delay().run_async(context)
            else:
                action.with_context(context).run()


class StateObjectMixin(object):
    """
    Mixin class that can be used to define a state object
    that can be used as a crapo_state

    Should be use as a mixin class in existing objects
    """

    automaton = fields.Many2one(
        comodel_name="crapo.automaton",
        default=lambda self: self._get_default_automaton(),
        store=True,
        required=True,
        index=True,
    )

    default_state = fields.Boolean(
        help="Might be use as default stage.", default=False, store=True
    )

    # Transitions (inverse relations)

    transitions_to = fields.One2many(
        string="Incomint transitions",
        comodel_name="crapo.transition",
        inverse_name="to_state",
    )

    transitions_from = fields.One2many(
        string="Outgoing transitions",
        comodel_name="crapo.transition",
        inverse_name="from_state",
    )
    # computed field to identify start and end states

    is_start_state = fields.Boolean(
        "Start State",
        compute="_compute_is_start_state",
        store=True,
        index=True,
    )

    is_end_state = fields.Boolean(
        "End State", compute="_compute_is_end_state", store=True, index=True
    )

    readonly_fields = fields.Char(
        help="List of model's fields name separated by comma"
    )

    @api.depends("transitions_to", "automaton")
    def _compute_is_start_state(self):
        for record in self:
            if (
                len(record.transitions_to) == 0
                or record.transitions_to is False
            ):
                record.is_start_state = True
            else:
                record.is_start_state = False

    @api.depends("transitions_from", "automaton")
    def _compute_is_end_state(self):
        for record in self:
            if (
                len(record.transitions_to) == 0
                or record.transitions_to is False
            ):
                record.is_end_state = True
            else:
                record.is_end_state = False

    def _do_search_default_automaton(self):
        return False

    @api.model
    def _get_default_automaton(self):
        default_value = 0
        if "current_automaton" in self.env.context:
            try:
                default_value = int(self.env.context.get("current_automaton"))
            except Exception:
                default_value = 0
        else:
            return self._do_search_default_automaton()

        return self.env["crapo.automaton"].browse(default_value)


class WrappedStateMixin(StateObjectMixin):
    """
    Mixin class that can be used to define a state object that
    wraps an existing model defining a state for another model

    The wrapped object can be used as a crapo_state

    Should be use as a mixin class in existing objects
    """

    _inherits = {"crapo.state": "crapo_state"}

    crapo_state = fields.Many2one(
        comodel_name="crapo.state",
        string="Related Crapo State",
        store=True,
        index=True,
        required=True,
        ondelete="cascade",
    )

    def _do_search_default_automaton(self):
        """
        finds or creates the default automaton (one per model)
        """
        automaton_model = self.env["crapo.automaton"]
        my_model = self.env["ir.model"].search(
            [("model", "=", self._state_for_model)], limit=1
        )
        my_automaton = automaton_model.search([("model_id", "=", my_model.id)])
        if not my_automaton:
            my_automaton = automaton_model.create(
                {
                    "name": "Automaton for {}".format(self._state_for_model),
                    "model_id": my_model.id,
                }
            )
        return my_automaton

    def _compute_related_state(
        self, values={}
    ):  # pylint: disable=dangerous-default-value
        """
        Create a new crapo_state for an existing record of the WrappedState
        """
        my_automaton = self._do_search_default_automaton()

        if not self.crapo_state:
            if not my_automaton:
                return False
            else:
                if "name" not in values:
                    values["name"] = "Default State for %s" % self.id
                values["automaton"] = my_automaton.id
                return self.env["crapo.state"].create(values)
