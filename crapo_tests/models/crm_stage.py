# coding: utf-8

"""
©2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""


from odoo import models, fields, api
from odoo.addons.base_crapo_workflow.mixins import crapo_automata_mixins

import logging

class CrmStageWithMixin(crapo_automata_mixins.WrappedStateMixin,models.Model):
    _inherit = "crm.stage"
    _state_for_model = "crm.lead"

    def write(self, values):
        logging.error("WRITING THE STUFF .... %s",str(self))
        if len(self) == 1:
            if 'crapo_state' not in values and not self.crapo_state:
                if 'name' in values:
                    vals={'name':values['name']}
                else:
                    vals={'name':self.name}
                mystate = self._compute_related_state(vals)
                values['crapo_state'] = mystate.id
            
        return super(CrmStageWithMixin, self).write(values)

    @api.model
    def create(self,values):
        if 'crapo_state' not in values and not self.crapo_state:
            if 'name' in values:
                vals={'name':values['name']}
            mystate = self._compute_related_state(vals)
            values['crapo_state'] = mystate.id
        
        return super(CrmStageWithMixin,self).create(values)