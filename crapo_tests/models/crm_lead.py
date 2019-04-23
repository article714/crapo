"""
©2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""


from odoo import models, fields, api
from odoo.addons.base_crapo_workflow.mixins import crapo_automata_mixins

import logging


class CrmLeadWithMixin(crapo_automata_mixins.ObjectWithStateMixin,
                       models.Model):
    _inherit = "crm.lead"
    _sync_state_field = "stage_id"

    state = fields.Many2one(compute="_compute_synchronize_state", store=True)

    @api.depends("stage_id")
    def _compute_synchronize_state(self):

        for record in self:
            record.state = record.stage_id.crapo_state

    def _get_sync_state(self, newid):
        return self.env['crm.stage'].browse(newid).crapo_state.id

    def _get_default_state(self):

        default_stage_id = self._default_stage_id()
        default_stage = None
        if default_stage_id:
            default_stage = self.env["crm.stage"].browse(default_stage_id)

        if default_stage is not None and default_stage.crapo_state:
            return default_stage.crapo_state
        else:
            return crapo_automata_mixins.ObjectWithStateMixin._get_default_state(self)

    @api.multi
    def write(self, values):
        self.pre_write_checks(values)
        super(CrmLeadWithMixin, self).write(values)
