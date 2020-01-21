"""
©2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""


from odoo import models, fields, api
from odoo.addons.crapo_automaton.mixins.crapo_automata_mixins import (
    ObjectWithStateMixin,
)


class CrmLeadWithMixin(ObjectWithStateMixin, models.Model):
    _inherit = "crm.lead"
    _sync_state_field = "stage_id"

    state = fields.Many2one(compute="_compute_synchronize_state", store=True)

    @api.depends("stage_id")
    def _compute_synchronize_state(self):

        for record in self:
            record.state = record.stage_id.crapo_state

    def _get_sync_state(self, newid):
        return self.env["crm.stage"].browse(newid).crapo_state.id

    def _get_default_state(self):

        default_stage_id = self._default_stage_id()
        default_stage = None
        if default_stage_id:
            default_stage = self.env["crm.stage"].browse(default_stage_id)

        if default_stage is not None and default_stage.crapo_state:
            return default_stage.crapo_state
        else:
            return ObjectWithStateMixin._get_default_state(self)

    @api.multi
    def write(self, values):
        if self._sync_state_field in values and "state" not in values:
            values["state"] = self._get_sync_state(
                values[self._sync_state_field]
            )

        return super(CrmLeadWithMixin, self).write(values)
