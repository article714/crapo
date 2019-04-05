# coding: utf-8

"""
©2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""


from odoo import models, fields
from odoo.addons.base_crapo_workflow.mixins import crapo_automata_mixins


class CrmStageWithMixin(crapo_automata_mixins.WrappedStateMixin,models.Model):
    _inherit = "crm.stage"
    _state_for_model = "crm.lead"
