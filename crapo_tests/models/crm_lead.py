# coding: utf-8

"""
©2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""


from odoo import models
from odoo.addons.base_crapo_workflow.mixins import crapo_automata_mixins

import logging

class CrmLeadWithMixin(crapo_automata_mixins.ObjectWithStateMixin,models.Model):
    _inherit = "crm.lead"


    def _get_default_state(self):

        default_stage_id = self._default_stage_id()
        default_stage = None
        if default_stage_id:
            default_stage = self.env["crm.stage"].browse(default_stage_id)

        logging.error("PRROUROUROUT %s => %s (%s / %s)",str(self),str(self._name),str(self.automaton),str(default_stage))

        if default_stage is not None and default_stage.crapo_state:
            logging.error("AND THE WINNER IS %s ",str(default_stage.crapo_state))
            return default_stage.crapo_state
        else:
            return crapo_automata_mixins.ObjectWithStateMixin._get_default_state(self)
