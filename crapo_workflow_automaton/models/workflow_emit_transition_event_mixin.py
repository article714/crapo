from odoo import models
import logging


class CrapoWorkflowAutomatonMixin(models.AbstractModel):
    """
        Do at least the same things as the mixin crapo.automaton.mixin
        and in addition emit the transition event for crapo_state_id changes
    """

    _name = "crapo.workflow.automaton.mixin"
    _inherit = "crapo.automaton.mixin"

    def write(self, values):

        sync_state_field = self[:1].crapo_automaton_id.sync_state_field

        if "crapo_state_id" in values or sync_state_field in values:
            records_pre_write_crapo_state = (
                self._get_current_crapo_state_for_records()
            )

        res = super(CrapoWorkflowAutomatonMixin, self).write(values)

        if "crapo_state_id" in values or sync_state_field in values:
            self._emit_transtion_event_for_records(
                records_pre_write_crapo_state
            )

        return res

    def _get_current_crapo_state_for_records(self):
        crapo_states = {}
        for rec in self:
            crapo_states[rec.id] = rec.crapo_state_id
        return crapo_states

    def _emit_transtion_event_for_records(self, records_previous_crapo_state):
        for rec in self:
            from_state = records_previous_crapo_state[rec.id]

            rec.wf_event(
                "transition",
                {
                    "from_state": from_state.id,
                    "to_state": rec.crapo_state_id.id,
                    "record": rec,
                },
            )
